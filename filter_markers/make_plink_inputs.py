# -*- coding: utf-8 -*-
'''
Retrieves Mouse Diversity Array genotypes from database in PLINK format

Usage: plink.py <file with list of strains>
Output: .tped and .tfam
'''

import pyodbc
import os
import sys
import time

server_name = 'PARKSLAB'
db = 'HMDP'

# Warn if file already exists
def warn_if_overwrite(output_fn):
	if os.path.isfile(output_fn):
		print('\tThe file \'' + output_fn + '\' already exists, and will be overwritten in 3 seconds (press Ctrl + C to prevent overwrite)')
		time.sleep(3)

def get_genotypes(strains, iids, output_fn):
	# Uses 0 as genetic distance (centimorgans) for all snps
	query_template = '''select snp_chr, rsID, 0 AS centimorgans, snp_bp_mm10, %s
	from HMDP.dbo.genotype_calls_plink_format
	order by snp_chr, snp_bp_mm10
	'''
	# warn_if_overwrite(output_fn)

	# Create file for TPED
	outfile = open(output_fn, 'w')
	c = pyodbc.connect(SERVER=server_name,DATABASE=db,DRIVER='{SQL Server Native Client 11.0}',Trusted_Connection='Yes')
	q = query_template % ', '.join(['[%s]' % x for x in strains])

	print('\tQuerrying %s on SQL-server %s' % (db,server_name) )
	t0 = time.clock()	# see how long query took
	res = c.execute(q)
	print('\tQuery completed in %.3f minutes' % ((time.clock()-t0)/60) )

	tfam = 0
	linebuffer = []
	# maybe retrieve all rows, then print at end
	for row in res:
		# generate .tfam file for PLINK
		if tfam == 0:
			# sanitize strain names
			colnames = [t[0] for t in row.cursor_description]
			colnames = [x.replace('/', '.').replace(' ', '.') for x in colnames]

			tfam_output_fn = output_fn.replace('.tped', '.tfam')
			warn_if_overwrite(tfam_output_fn)
			tfam_outfile = open(tfam_output_fn, 'w')
			print('\tWriting to', tfam_output_fn)
			# accesses list of strains by referring to table's column names
			for i, fid in enumerate(colnames[4:]):
				if iids is None:
					iid = (i+1)
				else:
					iid = iids[i].replace('/', '.').replace(' ', '.')
				# sets most fields in file to "missing"
				tfam_outfile.write('\t'.join(map(str, [fid, iid, 0, 0, 0, -9]))+'\n' )
			tfam_outfile.close()
			print('\tDone writing to',tfam_output_fn,
					'\n\tWriting to', output_fn)
			tfam = 1

		linebuffer.append('\t'.join(map(str, row)))
		# print 50000 lines at a time
		if len(linebuffer) == 50000:
			outfile.write('\n'.join(linebuffer)+'\n' )
			outfile.flush()
			linebuffer = []

	# flush lines if any are left over
	if linebuffer:
		outfile.write('\n'.join(linebuffer) )

	c.close()
	outfile.close()
	print('\tDone writing to', output_fn)

if __name__ == '__main__':
	num_args = len(sys.argv)
	if num_args < 2:
		print('\tUsage:', os.path.basename(sys.argv[0]), '<strains_file>')
	else:
		for filename in sys.argv[1:]:
			print ('\tProcessing', filename)
			f = open(filename)
			# strip() removes whitespace from beginning/end of linebuffer
			# split() returns list of words in string, parsed using parameter char.
			lines = [x.strip().split('\t') for x in f.readlines() if x.strip()]
			f.close()

			try:
				strains, iids = zip(*lines)
			except ValueError:
				print('\tError:',os.path.basename(sys.argv[1]), 'must have format <strain> TAB <IID>',)
				print('\tThe IIDS will be auto-generated.')
				iids = None
				# Convert lines to strings
				strains =[]
				for x in lines:
					strains.append(''.join(x))
			output_fn = '%s.tped' % os.path.splitext(filename)[0]
			get_genotypes(strains, iids, output_fn)
			print ('\tDONE')