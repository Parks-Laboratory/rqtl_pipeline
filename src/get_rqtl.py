# -*- coding: utf-8 -*-
'''
Retrieves Mouse Diversity Array genotypes from database in R/QTL format

Usage: get_rqtl.py  <csv with phenotype data> <file with list of markers> <output dir.>
	Inputs:
		-file containing the list of markers, one on each line
		-file containing lines of phenotype data:
			-format: Mouse ID,id,Sex,<phenotype 1>,...,<phenotype 2>
	Output:
		<main_geno_filename_prefix><geno_filename_suffix>
			e.g. "main_geno_csvsr.csv"
		<female pheno_filename_prefix><pheno_filename_suffix>
			e.g. "female_pheno_csvsr.csv"
		<male pheno_filename_prefix><pheno_filename_suffix>
		<hetero pheno_sexes_filename_prefix><pheno_filename_suffix>

Notes:
	get_genotypes() is dependent on results from get_phenotypes()

Future ideas:
	-Create temporary table in databse w/ all the markers, using the marker
	as primary key. Later, use this table in get_genotypes() query instead of
	the massive WHERE clause which currently has thousands of conditions per query
	-May be able to simplifiy script using Pandas Scientific Computing library
	-Script can be vastly simplified if phenotype data stored in database
'''
import pyodbc
import os
import sys
import time				# for script-duration stats presented to user
import string
from decimal import *	# for fixed-point representation
from math import *		# for rounding
import re				# for determining true count of significant digits
						# in a numeric string

#######################################################
##   Global fields (do not change):
#######################################################
make_chromosome_files = False	# No testing done on building geno chromosome files!
chromosomes = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','x']

output_dir = None
first_strain_column_index = 3	# see note on inputs in script description
rqtl_id_label = 'id'			# column label expected by R/QTL column with iids
rqtl_sex_label = 'sex'			# column label expected by R/QTL column with sexes
empty_string = ''
query_batch_size = 2000			# more than 2000 makes genotypes query too complex
max_buffer_size = 50000			# number rows to write to file at a time
female = 'female'
male = 'male'
hetero = 'hetero'
sex_label_as_numeric = {female:0,male:1}		# maps sex labels to numeric indicator

#######################################################
##   Parameters set by user (change as desired/needed):
#######################################################
sql_server_name = 'PARKSLAB'
db = 'HMDP'
genotype_source = '[dbo].[rqtl_csvsr_geno_format]'	# table or view name that provides data
marker_order_source = '[dbo].[genotypes]'			# table that provides order of markers

# columns used in query, must match column names in <genotype_source> and/or marker_order_source
marker_identifier = 'rsID'
marker_chromosome = 'snp_chr'
centiMorgans = 'cM_est_mm10'
marker_base_pair_position = 'snp_bp_mm10'	# used to estimate centimorgans
marker_quality_condition = " WHERE flagged = 0 and quality = 'good'"

# template-components for names of output files:
pheno_filename_prefixes = {female:'female',male:'male',hetero:'hetero'}	# change quoted parts only
pheno_filename_suffix = 'csvsr_pheno.csv'
main_geno_filename_prefix = 'main'
geno_filename_suffix = 'csvsr_geno.csv'

#######################################################
##   Main program:
#######################################################

class File_builder(object):
	'''
	Deals with formatting useful for all files, and in particular the main
	genotype file and each of the chromosome files
	'''
	column_labels = None
	column_labels_by_iid = None
	column_labels_by_strain = None
	formatted_row = None

	def __init__(self, name, fn_template):
		self.name = name.lower()
		self.file = None
		self.filename = os.path.normpath( '%s/%s_%s' % ( output_dir, self.name, fn_template ) )
		self.linebuffer = []

	def open(self):
		'''Opens file for writing'''
		self.file = open(self.filename, 'w')

	def append(self, row):
		'''Adds a row returned by query to the linebuffer'''
		sys.exit('Error: append() is abstract function')
		return

	def write_linebuffer(self):
		'''Writes the linebuffer to file (when buffer is full)'''
		self.file.write('\n'.join(self.linebuffer) + '\n')
		self.file.flush()
		self.linebuffer = []


class Geno_file_builder(File_builder):
	'''
	Deals with formatting useful for building genotype files
	'''
	def __init__(self, name, fn_template, data_by_strain):
		'''data_by_strain: an object of class Strains'''
		self.data_by_strain = data_by_strain
		super().__init__(name, fn_template)

	def append(self, row):
		'''Adds a row returned by query to the linebuffer'''
		# Intent is that rows are formatted once and re-used for main genotype file
			# and any chromosome file that is to be made
		# Each column belongs to an individual, with multiple individuals possible
		# 	in each strain. Therefore, genotype data is often duplicated
		if Geno_file_builder.formatted_row is None:
			new_row = []
			for index, marker_info in enumerate(Geno_file_builder.column_labels_by_strain[ :first_strain_column_index]):
				new_row.append(row[index])
			for index, strain in enumerate(Geno_file_builder.column_labels_by_strain[first_strain_column_index: ]):
				genotype = row[first_strain_column_index + index]
				individuals = self.data_by_strain.strains[strain]	# list of individual ids for that strain
				for individual in individuals:
					new_row.append(genotype)
			Geno_file_builder.formatted_row = ','.join(map(str, new_row))	# delimit columns with commas
		self.linebuffer.append(Geno_file_builder.formatted_row)

	def write_column_labels(self, column_labels):
		'''
		Sanitize strain names, remove marker_chromosome and
		centiMorgan column names to match R/QTL input format.
		'''

		# column labels for use by append()
		Geno_file_builder.column_labels_by_strain = column_labels[ :first_strain_column_index]

		# Intent is that column-names are formatted once and re-used for any
			# chromosome files that are to be made
		if Geno_file_builder.column_labels_by_iid is None:
			new_column_labels = []
			for name in column_labels[ :first_strain_column_index]:
				name = name.replace(marker_chromosome, empty_string)
				name = name.replace(centiMorgans, empty_string)
				new_column_labels.append(name)
			for strain in column_labels[first_strain_column_index: ]:
				# save order of strain column labels for use in append()
				Geno_file_builder.column_labels_by_strain.append(strain)
				individuals = self.data_by_strain.strains[strain]	# list of individual ids for that strain
				for individual in individuals:
					new_column_labels.append(individual.iid)
			# save sanitized column labels for reference when writing genotype rows
			Geno_file_builder.column_labels_by_iid = ','.join( new_column_labels )
		self.file.write(Geno_file_builder.column_labels_by_iid + '\n')
		# print(Geno_file_builder.column_labels_by_strain)


class Pheno_file_builder(File_builder):
	'''
	Deals with formatting useful for building phenotype files
	'''
	def __init__(self, sex, fn_template):
		name = sex	# default for pheno file builder that creates only a list of phenotype names
		if sex in pheno_filename_prefixes:
			name = pheno_filename_prefixes[sex]
		super().__init__(name, fn_template)
		self.sex = sex
		self.row = []

	def append(self, row):
		'''Adds a row returned by query to the linebuffer'''
		# delimit columns with commas
		self.linebuffer.append(','.join(map(str, row)) )
		self.row = []

	def do_sexes_match(self, individual):
		'''Check to see if an individual belongs in this pheno file'''
		both_female = self.sex == female and individual.is_female()
		both_male = self.sex == male and individual.is_male()
		both_sexes = self.sex == hetero		# anything goes
		return( both_female or both_male or both_sexes )


class Individual(object):
	iid_column_index = 0
	strain_column_index = 1
	sex_column_index = 2
	first_phenotype_column_index = 3
	row_names = None
	missing_value = '-'
	special_rows = [rqtl_sex_label, rqtl_id_label]

	def __init__(self, line):
		self.iid = sanitize(line[Individual.iid_column_index])
		self.strain = line[Individual.strain_column_index]
		self.sex = sex_label_as_numeric[line[Individual.sex_column_index].lower()]
		self.rows = []

	def add(self, line):
		for phenotype_value in line[Individual.first_phenotype_column_index: ]:
			self.rows.append( Individual.replace_missing_value(phenotype_value) )
		self.rows.append(self.sex)
		self.rows.append(self.iid)

	def is_female(self):
		return( self.sex == sex_label_as_numeric[female] )

	def is_male(self):
		return( self.sex == sex_label_as_numeric[male] )

	def replace_missing_value(value):
		'''
		Return value if it is numeric, otherwise return string indicating
		missing-value. Will return missing value for fractions.
		'''
		if not is_numeric(value):
			value = Individual.missing_value
		return(value)

class Individual_averaged(Individual):
	'''
	Stores phenotype data for all individuals of same sex of a single strain.
	Alternative to Individual class for when phenotype values are to be averaged.
	'''
	def __init__(self, line, sex_label):
		self.strain = line[Individual.strain_column_index]
		self.sex = sex_label_as_numeric[sex_label.lower()]
		# Differentiate male and female column labels for each strain
		iid = [sanitize(self.strain)]
		if sex_label == female:
			iid.append('f')
		elif sex_label == male:
			iid.append('m')
		self.iid = '.'.join(iid)
		# all lines are phenotypes except sex and iid
		num_phenotype_rows = len(line)-Individual_averaged.first_phenotype_column_index
		self.rows = [Individual_averaged.missing_value]*num_phenotype_rows
		self.rows.append(self.sex)
		self.rows.append(self.iid)

	def add(self, line):
		'''
		Append phenotype values to list of phenotypes
		'''
		for phenotype_index, phenotype_value in enumerate(line[Individual_averaged.first_phenotype_column_index: ]):
			# replace non-numeric phenotype value with string indicating missing-value
			phenotype_value = Individual_averaged.replace_missing_value(phenotype_value)

			# append value only if it is a number
			if phenotype_value != Individual_averaged.missing_value:
				# append value to existing list of values
				existing_phenotype_value = self.rows[phenotype_index]
				if(existing_phenotype_value == Individual_averaged.missing_value):
					self.rows[phenotype_index] = []
				self.rows[phenotype_index].append(phenotype_value)

	def average(self, phenotype_values):
		'''
		Returns average of a list of phenotype values. The parameter is used to
		simplify the process of specifying which
		'''
		# context set globally for all Decimal arithmetic, not just for this instance of method
		setcontext( Context( prec=None, rounding=None ) )
		# check if no values to average
		if len(phenotype_values) == 1 and phenotype_values[0] == Individual_averaged.missing_value:
			return( Individual_averaged.missing_value )

		sum_phenotype_values = Decimal('0')
		num_phenotypes = Decimal('0')
		min_significant_figures = Decimal('+Inf')
		for phenotype_value in phenotype_values:
			# find operand with fewest significant figures
			sigfig_count = num_sigfigs(phenotype_value)
			if sigfig_count < min_significant_figures:
				min_significant_figures = sigfig_count

			# add value to sum
			sum_phenotype_values = sum_phenotype_values + Decimal(phenotype_value)
			num_phenotypes = num_phenotypes + 1
		# context set globally for all Decimal arithmetic, not just for this instance of method
		setcontext( Context( prec=min_significant_figures, rounding=ROUND_HALF_EVEN) )
		# calculate average, round based on min_significant_figures
		average = sum_phenotype_values / num_phenotypes
		# find out if answer has a decimal poin
		return( str(average) )


class Strains(object):
	'''For each strain, stores phenotype data for individual (either averaged or not)'''

	def __init__(self, average_by_strain):
		'''average_by_strain: True or False'''
		self.average_by_strain = average_by_strain
		self.strains = {}
		self.ordered_strains = []

	def append(self, line):
		'''Function through which individuals(either averaged or not) are created'''
		if self.average_by_strain:
			self.append_averaged_by_strain(line)
		else:
			self.append_not_averaged_by_strain(line)

	def append_averaged_by_strain(self, line):
		'''
		Creates infrastructure to store male and female data separately.

		Each individual's data is added to either the male list or female list
		for the strain they belong to. Later, in Individual_averaged.average(),
		all values in male list get averaged and all values in female list get
		averaged.

		Adds new strain to an ordered list which is used in get_phenotypes()
		and get_genotypes().
		'''
		strain = line[Individual_averaged.strain_column_index]
		sex = sex_label_as_numeric[ line[Individual_averaged.sex_column_index].lower() ]
		if strain not in self.strains:
			# create list w/ 2 elements and index into it using numeric indicators of sex
			sexes = []
			sexes.append(Individual_averaged(line, female))
			sexes.append(Individual_averaged(line, male))
			self.strains[strain] = sexes
			self.ordered_strains.append(strain)
		self.strains[strain][sex].add(line)	# add line of data to Individual_averaged object

	def append_not_averaged_by_strain(self, line):
		'''
		Creates an individual with the given line of phenotype data.
		Adds new strain to an ordered list which is used in get_phenotypes()
		and get_genotypes().
		'''
		strain = line[Individual.strain_column_index]
		if strain not in self.strains:
			self.strains[strain] = []
			# set order of strains for use by get_phenotypes() and get_genotypes()
			self.ordered_strains.append(strain)
		individual = Individual(line)
		individual.add(line)	# add line of data to Individual object
		self.strains[strain].append(individual)


def num_sigfigs(value):
	'''
	Counts number of significant figures in a numeric string.
	TODO: replace regex w/ conditional logic (regex decreased efficiency by 10%)
	'''
	# remove scientific notation characters
		# -03.05E+4 -> 03.05
	parsed_value = re.sub(r'^-*((\d+\.?\d*)|(\d*\.\d+)).*$', r'\1', value)
	# remove leading zeroes to left of decimal point, keeping at most 1 zero
		# e.g. -03.05E+4 -> 305E+4    or    05 -> 5    or   0.4 -> .4    or   00 -> 0
	parsed_value = re.sub(r'^0*(\d.*)$', r'\1', parsed_value)
	# remove leading zeroes to right of decimal point, plus any immediately to
	# the left of decimal point, if value < 1
		# e.g. .05E+4 -> 5E+4    or   0.01 -> .1
	parsed_value = re.sub(r'^0*(\.)0*(\d+)$', r'\1\2', parsed_value)
	# remove trailing zeroes to right of integer w/ no decimal point
		# e.g. 100 -> 1   but   100. -> 100.
	parsed_value = re.sub(r'^([1-9]+)0*$', r'\1', parsed_value)
	# remove decimal point
	parsed_value = re.sub(r'\.', r'', parsed_value)
	return( len(parsed_value) )

def is_numeric(string):
	try:
		Decimal(string)
		return(True)
	except InvalidOperation:
		return(False)

def sanitize(dirty_string):
	'''Remove undesirable characters from a string'''
	output_string = dirty_string
	replacement = '_'
	duplicated_replacement = replacement + replacement
	undesired_characters = '!"#$&\'()*+,-/:;<=>?@[\\]^`{|}~' + string.whitespace

	# whitespace @front/back of string has no purpose; needs no replacement
	output_string = output_string.strip()

	# replace problem characters
	for undesired_character in undesired_characters:
		output_string = output_string.replace(undesired_character, replacement)

	# replace characters that are only problematic at the end of a string
	#	e.g. periods are problematic when they are last char. of file/dir. name
	undesired_ending_characters = '._'
	if output_string[len(output_string)-1] in undesired_ending_characters:
		output_string = output_string[ :len(output_string)-1]

	# handle special cases
	output_string = output_string.replace('%','percent')

	# fix mess made by replacement (i.e., duplicated repalcement characters)
	while duplicated_replacement in output_string:
		output_string = output_string.replace(duplicated_replacement, replacement)

	return( output_string )


def sanitize_list(string_list):
	'''Iterates over a list of strings, sanitizing each in turn'''
	for index, string in enumerate(string_list):
		string_list[index] = sanitize(string)
	return(string_list)


def sort_markers( markers_raw, connection ):
	'''Query database for correct order of markers, according to bp position'''

	# query for correct order of markers
	query_for_marker_order = 'SELECT ' + marker_identifier +\
						  ' FROM ' + marker_order_source +\
						  marker_quality_condition +\
						  ' ORDER BY ' +  marker_chromosome +','+  marker_base_pair_position

	ordering = connection.execute(query_for_marker_order)

	# build list of ordered markers
	markers_ordered = []
	for row in ordering:
		marker = empty_string.join(map(str,row))
		# filter sorted markers to just the ones specified in markers input file
		if marker in markers_raw:
			markers_ordered.append(marker)
			markers_raw.pop(marker)		# ensure that each marker_identifier is unique/included only once
	return(markers_ordered)


def sql_format(list):
	'''Format a list for use in an sql query's where-clause'''
	return( '[' + '],['.join(list) + ']')


def rqtl_format(list):
	'''Sanitize strain names'''
	new_list = []
	for item in list:
		new_list.append(item.replace('/','.'))
	return(new_list)


def get_genotypes( data_by_strain, markers_raw, geno_fn_template ):
	'''Main function for building genotype file(s)'''
	num_markers = len(markers_raw)

	# create dictionary holding <file name>:<Geno_file_builder object> pairs
	files = {}

	filenames = [main_geno_filename_prefix]
	# open files for writing
	if make_chromosome_files:
		filenames = filenames + chromosomes

	# for main geno file and (if make_chromosome_files = True) also chromosome files
	for filename in filenames:
		files[filename] = Geno_file_builder(filename, geno_fn_template, data_by_strain)
		files[filename].open()

	# connect to database
	connection = pyodbc.connect(SERVER=sql_server_name
		,DATABASE=db
		,DRIVER='{SQL Server Native Client 11.0}'
		,Trusted_Connection='Yes')

	'''
	Sort markers, not b/c this guarrantees the query will return them in this order
	but so that the block returned by the query will contain the correct subset
	of markers to be written to file
	'''
	markers_ordered = sort_markers( markers_raw, connection )
	ordered_strains_formatted = sql_format(data_by_strain.ordered_strains)

	# Assemble rqtl input files
	column_labels = None
	next_row_to_get = 0
	linebuffer = []
	while next_row_to_get < num_markers :
		# used to select subset of markers to get in this query
		max_rows_to_get = next_row_to_get + query_batch_size
		if max_rows_to_get > num_markers:
			max_rows_to_get = num_markers

		# format subset of markers for query's where-clause.
			# Format: markers =   "marker = 'marker_1' or marker = 'marker_2' or...marker = 'marker_n'"
		markers = marker_identifier + ' = \'' + ('\' or ' + marker_identifier + ' = \'').join(
			marker for marker in markers_ordered[next_row_to_get:max_rows_to_get]) + '\''

		query_for_genotype_data = ('SELECT ' + marker_identifier +' as id,'+
				marker_chromosome +','+  centiMorgans +','+ ordered_strains_formatted +
				' FROM ' + genotype_source +
				' WHERE ' + markers +
				' ORDER BY ' +  marker_chromosome +','+  centiMorgans)
					# ORDER BY needed b/c rqtl assumes markers are in correct order
		data = connection.execute(query_for_genotype_data)	# cursor object

		# write header of all geno files on first iteration
		if next_row_to_get == 0:
			# for all files: get list of column names
			column_labels = [column[0] for column in data.description]

			for geno_file_builder in files.values():
				geno_file_builder.write_column_labels(column_labels)

		# Process query data one row at a time, writing to files when buffers are full
		for row in data:
			# open file for chromosome if needed, initialize its associated object,
				# and add it to the list of geno_file_builders
			geno_file_builders_to_alter = [ files[main_geno_filename_prefix] ]

			chromosome = None
			if make_chromosome_files == True:
				# each marker's chromosome name is in column 1 of each row
				chromosome = files[row[1].lower()]
				geno_file_builders_to_alter.append(chromosome)

			# write linebuffer to file if linebuffer is full
			Geno_file_builder.formatted_row = None
			for geno_file_builder in geno_file_builders_to_alter:
				geno_file_builder.append(row)
				if len(geno_file_builder.linebuffer) == max_buffer_size:
					geno_file_builder.write_linebuffer()

		# write remaining lines if buffers full or query-processing is done
		for geno_file_builder in files.values():
			if max_rows_to_get == num_markers or len(geno_file_builder.linebuffer) == max_buffer_size:
				geno_file_builder.write_linebuffer()

		next_row_to_get = max_rows_to_get

	# close all files
	for geno_file_builder in files.values():
		geno_file_builder.file.close()

	connection.close()


def get_phenotypes( lines, pheno_fn_template, use_average_by_strain ):
	'''Main function for building phenotype files'''
	Individual.row_names = (sanitize_list(lines[0][Individual.first_phenotype_column_index: ] +
						[rqtl_sex_label] + [rqtl_id_label]) )

	# determines if data will be read in and grouped by strain or kept separated by individual
	data_by_strain = Strains(use_average_by_strain)
	# store iid, sex, strain, and phenotype values for each strain in its own object
	for line in lines[1: ]:
		data_by_strain.append(line)	# also for expanding strain in get_genotypes()

	# open files for writing:
	phenotype_list_builder = Pheno_file_builder('phenotypes', 'list.txt')
	phenotype_list_builder.open()	# file w/ just the list of sanitized phenotypes
	sexes = [female, male, hetero]
	pheno_file_builders = []
	for sex in sexes:
		pheno_file_builder = Pheno_file_builder(sex, pheno_fn_template)
		pheno_file_builder.open()
		pheno_file_builders.append(pheno_file_builder)

	# work left to right across iids, accessing their phenotypes as you go and
	# use condition to write blank instead of data when appropriate
	for row_index, row_name in enumerate(Individual.row_names):
		# for file containing only the list of phenotypes, don't include sex or id labels:
		if row_name not in Individual.special_rows:
			phenotype_list_builder.row.append(row_name)
			phenotype_list_builder.append( phenotype_list_builder.row )
		# for rqtl pheno input files:
		ordered_strains = data_by_strain.ordered_strains
		for strain_index, strain in enumerate(ordered_strains):
			individuals = data_by_strain.strains[strain]
			for individual_index, individual in enumerate(individuals):
				for pheno_file_builder in pheno_file_builders:
					# append row_names prior to appending data for first individual
					if pheno_file_builder.row == []:
						pheno_file_builder.row.append(row_name)
					'''row_value is a single value for non-averaged inidividual
					and a list of not-yet-averaged values for to-be-averaged individual'''
					row_value = individual.rows[row_index]
					write_row_value = ( pheno_file_builder.do_sexes_match(individual)
						or row_name in Individual.special_rows
						and not row_value == Individual.missing_value )
					if ( write_row_value ):
						if use_average_by_strain and row_name not in Individual_averaged.special_rows:
							# pass list of not-yet-averaged phenotype values
							pheno_file_builder.row.append(individual.average(row_value))
						else:
							pheno_file_builder.row.append(row_value)
					else:
						# write empty string
						pheno_file_builder.row.append(Individual.missing_value)
					# add row to linebuffer
					is_last_strain = strain_index == len(ordered_strains)-1
					is_last_individual_of_strain = individual_index == len(individuals)-1
					if is_last_strain and is_last_individual_of_strain:
						pheno_file_builder.append( pheno_file_builder.row )

	# write file and close
	for pheno_file_builder in pheno_file_builders + [phenotype_list_builder]:
		pheno_file_builder.write_linebuffer()
		pheno_file_builder.file.close()

	return(data_by_strain)


if __name__ == '__main__':
	'''Entry point for program, reads input files, calls main functions'''
	num_args = len(sys.argv)
	if num_args < 4:
		# Display help message
		sys.exit('Usage: ' + os.path.basename( sys.argv[0] )
		+ ' <csv with phenotype data>  <file with list of markers>  <output dir.>  [-average]')
	else:
		output_dir = sys.argv[3]
		if( not os.path.isdir(output_dir) ):
			os.mkdir(output_dir)

		# Process input for pheno file:
		pheno_input_path = os.path.normpath( sys.argv[1] )
		pheno_file = open(pheno_input_path)

		use_average_by_strain = False
		if num_args == 5 and sys.argv[4] == '-average':
			use_average_by_strain = True

		pheno_lines = [line.strip().split(',') for line in pheno_file.readlines()]
		t0 = time.clock()	# see how long query took
		# Build phenotype files
		phenotype_data_by_strain = get_phenotypes( pheno_lines, pheno_filename_suffix, use_average_by_strain )
		print( 'Pheno files built in %.2f minutes' % ((time.clock()-t0)/60) )

		# Process input for geno file(s):
		geno_input_path = os.path.normpath( sys.argv[2] )
		geno_file = open(geno_input_path)

		geno_lines = [line.strip().split('\t') for line in geno_file.readlines() if line.strip()]
		geno_file.close()

		# Convert marker lines to strings, store in dictionary for fast lookup:
		markers = {}
		for line in geno_lines:
			markers[empty_string.join(line)] = None

		t0 = time.clock()	# see how long query took
		# Build genotype file(s)
		get_genotypes( phenotype_data_by_strain, markers, geno_filename_suffix )
		print( 'Geno file built in %.2f minutes' % ((time.clock()-t0)/60) )
