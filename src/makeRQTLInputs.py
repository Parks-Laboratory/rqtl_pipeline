# -*- coding: utf-8 -*-
'''
Retrieves Mouse Diversity Array genotypes from database in R/QTL format

Usage: get_rqtl.py  <csv with phenotype data> <file with list of markers> <output dir.>
	Inputs:
		1) File containing the list of markers, one on each line
			File Format:
				<marker 1>
				<marker 2>
				...
				<marker n>
		2) CSV containing phenotype data
			File format:
				Mouse ID,id,Sex,<phenotype label 1>,...,<phenotype label n>
				<individual id 1>,<strain id>,<Male/Female>,<phenotype 1>,...,<phenotype m>
				...
				<individual id n>,<strain id>,<Male/Female>,<phenotype 1>,...,<phenotype m>
			Note: Accepted scientific notation formats:
				-e.g. 1.23E3, 1.23E+3, 1.23E-3,
					1.23e3, 1.23e+3, 1.23e-3
					also, 12.3E3 is accepted, even though it's not proper
				-only digits, decimal points, and scientific notation symbols
				(e.g. E,+,-) are allowed
				(e.g. none of the following symbols are allowed: #%$(){}[]*=)
				-additionally, no whitespace (i.e. spaces or tabs)
				can exist within the value (e.g. 1.23 e4 is not legal)
	Outputs:
		Genotype file(s):
			Filename format:
				<Parameter.MAIN_GENO_FILENAME_PREFIX><Parameter.GENO_FILENAME_SUFFIX>
					e.g. "main_geno_csvsr.csv"
			File format:
				<Global.RQTL_ID_LABEL>,,,<1st individual's id>,...,<nth individual's id>
				<marker 1 id>,<chromosome #>,<centimorgans>,<1st individual's allele>,...,<mth individual's allele>
				...
				<marker n id>,<chromosome #>,<centimorgans>,<1st individual's allele>,...,<mth individual's allele>

		Phenotype files:
			Filename format:
				<female pheno_filename_prefix><Parameter.PHENO_FILENAME_SUFFIX>
					e.g. "female_pheno_csvsr.csv"
				<male pheno_filename_prefix><Parameter.PHENO_FILENAME_SUFFIX>
					e.g. "male_pheno_csvsr.csv"
				<hetero pheno_sexes_filename_prefix><Parameter.PHENO_FILENAME_SUFFIX>
					e.g. "hetero_pheno_csvsr.csv"
			File format:
				<trait 1>, <value for 1st individual>,...,<value for nth individual>
				...
				<trait n>, <1st individual's value>,...,<nth individual's value>
				<Global.RQTL_SEX_LABEL>,<1st individual's sex>,...,<nth individual's sex>
				<Global.RQTL_ID_LABEL>,<1st individual's id>,...,<nth individual's id>

Notes:
	-make_genotype_files() is dependent on results from make_phenotype_files().
	This is due to the contraint that R/QTL requires the columns of both
	input files to match up (i.e. order of individuals is same in both files)

Known issues:
	-Bug in code that split up genotype data so each data for each chromosome
	is in its own file

Future ideas:
	-Create temporary table in databse w/ all the markers, using the marker
	as primary key. Later, use this table in make_genotype_files() query instead of
	the massive WHERE clause which currently has thousands of conditions per query
	-May be able to simplifiy script using Pandas Scientific Computing library
	-Script can be vastly simplified if phenotype data stored in database
	-Re-implement completely:
		-If all phenotype and genotype data are in a database, create a view
		and just pull from that.
		-PRO(s): The benefit is that this script wouldn't need to provide functionality
		already implemented by the database engine (significantly, pivot function).
		-CON(s): This forces the user to first import all data to database
		(which will force user to clean up their data and titles first).
'''
import pyodbc
import os
import sys
import time				# for script-duration stats presented to user
import string
# for fixed-point representation:
from decimal import (Decimal, Context, InvalidOperation, ROUND_HALF_EVEN,
	getcontext, setcontext)
import re				# for determining true count of significant digits
						# in a numeric string
from enum import Enum

#######################################################
##   Global fields (do not change):
#######################################################
class Global():
	MAKE_CHROMOSOME_FILES = False	# Has bug where headings written but no genotyeps
	CHROMOSOMES = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','x']

	output_dir = None
	FIRST_STRAIN_COLUMN_INDEX = 3	# see note on inputs in script description
	RQTL_ID_LABEL = 'id'			# column label expected by R/QTL column with iids
	RQTL_SEX_LABEL = 'sex'			# column label expected by R/QTL column with sexes
	RQTL_MISSING_VALUE_LABEL = '-'
	EMPTY_STRING = ''
	QUERY_BATCH_SIZE = 2000			# more than 2000 makes genotypes query too complex
	MAX_BUFFER_SIZE = 50000			# number rows to write to file at a time
	FEMALE = 'female'
	MALE = 'male'
	HETERO = 'hetero'
	SEX_LABEL_AS_NUMERIC = {FEMALE:0,MALE:1}		# maps sex labels to numeric indicator

class Rounding_method(Enum):
	'''Adjusted by user in "Parameters set up user" section,
	used by Individual_averaged.average()'''
	# min = 'round_min'
	MAX = 'round max'
	NO_ROUNDING = 'no rounding'


#######################################################
##   Parameters set by user (change as desired/needed):
#######################################################
class Parameter():
	SQL_SERVER_NAME = 'PARKSLAB'
	DATABASE = 'HMDP'
	GENOTYPE_SOURCE_TABLE = '[dbo].[rqtl_csvsr_geno_format]'	# table or view name that provides data
	MARKER_ORDER_SOURCE_TABLE = '[dbo].[genotypes]'			# table that provides order of markers

	# columns used in query, must match column names in <Parameter.GENOTYPE_SOURCE_TABLE> and/or Parameter.MARKER_ORDER_SOURCE_TABLE
	MARKER_IDENTIFIER_COLUMN_NAME = 'rsID'
	MARKER_CHROMOSOME_COLUMN_NAME = 'snp_chr'
	CENTIMORGAN_COLUMN_NAME = 'cM_est_mm10'
	BP_POSITION_COLUMN_NAME = 'snp_bp_mm10'	# used to estimate centimorgans
	MARKER_QUALITY_CONDITION = " WHERE flagged = 0 and quality = 'good'"  # ensures uniqueness of marker

	# template-components for names of output files:
	PHENO_FILENAME_PREFIXES = {Global.FEMALE:'female',Global.MALE:'male',Global.HETERO:'hetero'}	# change quoted parts only
	PHENO_FILENAME_SUFFIX = 'csvsr_pheno.csv'
	MAIN_GENO_FILENAME_PREFIX = 'main'
	GENO_FILENAME_SUFFIX = 'csvsr_geno.csv'

	'''Specification for number of digits to keep after rounding an average of phenotype values)
		Options for ROUNDING_METHOD:
			Rounding_method.MAX: script looks at list of values to be averaged and keeps
							as many sigfigs as the value with most number sigfigs
							e.g. (1.00, 1.0, 1)/3 rounds to 1.00
							(3 sigfigs, non-deterministic # decimal digits)
			Rounding_method.NO_ROUNDING: no rounding done, max digits kept (Default: 28 digits)'''
	ROUNDING_METHOD = Rounding_method.MAX


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
		self.filename = os.path.normpath( '%s/%s_%s' % ( Global.output_dir, self.name, fn_template ) )
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
			for index, marker_info in enumerate(Geno_file_builder.column_labels_by_strain[ :Global.FIRST_STRAIN_COLUMN_INDEX]):
				new_row.append(row[index])
			for index, strain in enumerate(Geno_file_builder.column_labels_by_strain[Global.FIRST_STRAIN_COLUMN_INDEX: ]):
				genotype = row[Global.FIRST_STRAIN_COLUMN_INDEX + index]
				individuals = self.data_by_strain.strains[strain]	# list of individual ids for that strain
				for individual in individuals:
					new_row.append(genotype)
			Geno_file_builder.formatted_row = ','.join(map(str, new_row))	# delimit columns with commas
		self.linebuffer.append(Geno_file_builder.formatted_row)

	def write_column_labels(self, column_labels):
		'''
		Sanitize strain names, remove Parameter.MARKER_CHROMOSOME_COLUMN_NAME and
		centiMorgan column names to match R/QTL input format.
		'''

		# column labels for use by append()
		Geno_file_builder.column_labels_by_strain = column_labels[ :Global.FIRST_STRAIN_COLUMN_INDEX]

		# Intent is that column-names are formatted once and re-used for any
			# chromosome files that are to be made
		if Geno_file_builder.column_labels_by_iid is None:
			new_column_labels = []
			for name in column_labels[ :Global.FIRST_STRAIN_COLUMN_INDEX]:
				name = name.replace(Parameter.MARKER_CHROMOSOME_COLUMN_NAME, Global.EMPTY_STRING)
				name = name.replace(Parameter.CENTIMORGAN_COLUMN_NAME, Global.EMPTY_STRING)
				new_column_labels.append(name)
			for strain in column_labels[Global.FIRST_STRAIN_COLUMN_INDEX: ]:
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
		if sex in Parameter.PHENO_FILENAME_PREFIXES:
			name = Parameter.PHENO_FILENAME_PREFIXES[sex]
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
		both_female = self.sex == Global.FEMALE and individual.is_female()
		both_male = self.sex == Global.MALE and individual.is_male()
		both_sexes = self.sex == Global.HETERO		# anything goes
		return( both_female or both_male or both_sexes )


class Individual(object):
	iid_column_index = 0
	strain_column_index = 1
	sex_column_index = 2
	first_phenotype_column_index = 3
	row_names = None
	special_rows = [Global.RQTL_SEX_LABEL, Global.RQTL_ID_LABEL]

	def __init__(self, line):
		self.iid = sanitize(line[Individual.iid_column_index])
		self.strain = line[Individual.strain_column_index]
		self.sex = Global.SEX_LABEL_AS_NUMERIC[line[Individual.sex_column_index].lower()]
		self.rows = []

	def add(self, line):
		for phenotype_value in line[Individual.first_phenotype_column_index: ]:
			self.rows.append( Individual.replace_missing_value(phenotype_value) )
		self.rows.append(self.sex)
		self.rows.append(self.iid)

	def is_female(self):
		return( self.sex == Global.SEX_LABEL_AS_NUMERIC[Global.FEMALE] )

	def is_male(self):
		return( self.sex == Global.SEX_LABEL_AS_NUMERIC[Global.MALE] )

	def replace_missing_value(value):
		'''
		Return value if it is numeric, otherwise return string indicating
		missing-value. Will return missing value for fractions.
		'''
		if not is_numeric(value):
			value =  Global.RQTL_MISSING_VALUE_LABEL
		return(value)

class Individual_averaged(Individual):
	'''
	Stores phenotype data for all individuals of same sex of a single strain.
	Alternative to Individual class for when phenotype values are to be averaged.
	'''
	def __init__(self, line, sex_label):
		self.strain = line[Individual.strain_column_index]
		self.sex = Global.SEX_LABEL_AS_NUMERIC[sex_label.lower()]
		# Differentiate male and female column labels for each strain
		iid = [sanitize(self.strain)]
		if sex_label == Global.FEMALE:
			iid.append('f')
		elif sex_label == Global.MALE:
			iid.append('m')
		self.iid = '.'.join(iid)
		# all lines are phenotypes except sex and iid
		num_phenotype_rows = len(line)-Individual_averaged.first_phenotype_column_index
		self.rows = [ Global.RQTL_MISSING_VALUE_LABEL]*num_phenotype_rows
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
			if phenotype_value !=  Global.RQTL_MISSING_VALUE_LABEL:
				# append value to existing list of values
				existing_phenotype_value = self.rows[phenotype_index]
				if(existing_phenotype_value ==  Global.RQTL_MISSING_VALUE_LABEL):
					self.rows[phenotype_index] = []
				self.rows[phenotype_index].append(phenotype_value)

	def average(phenotype_values):
		'''
		Input: list of numeric strings
		Output: mean of those strings, as a string

		Returns average of a list of phenotype values. The parameter is used to
		simplify the process of specifying which
		'''
		# check if no values to average
		num_phenotype_values = len(phenotype_values)
		if num_phenotype_values == 1 and phenotype_values[0] ==  Global.RQTL_MISSING_VALUE_LABEL:
			return(  Global.RQTL_MISSING_VALUE_LABEL )

		# calculate average
		sum_phenotype_values = Significant_value.sum(phenotype_values)
		average = sum_phenotype_values / num_phenotype_values
		average_rounded = Significant_value.round(sum_phenotype_values, average, Parameter.ROUNDING_METHOD)
		return( str(average_rounded) )


class Strains(object):
	'''For each strain, stores phenotype data for individual (either averaged or not)'''

	def __init__(self, average_by_strain):
		'''Create Strain object
		Arguments:
		average_by_strain -- True or False'''
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

		Adds new strain to an ordered list which is used in make_phenotype_files()
		and make_genotype_files().
		'''
		strain = line[Individual_averaged.strain_column_index]
		sex = Global.SEX_LABEL_AS_NUMERIC[ line[Individual_averaged.sex_column_index].lower() ]
		if strain not in self.strains:
			# create list w/ 2 elements and index into it using numeric indicators of sex
			sexes = []
			sexes.append(Individual_averaged(line, Global.FEMALE))
			sexes.append(Individual_averaged(line, Global.MALE))
			self.strains[strain] = sexes
			self.ordered_strains.append(strain)
		self.strains[strain][sex].add(line)	# add line of data to Individual_averaged object

	def append_not_averaged_by_strain(self, line):
		'''
		Creates an individual with the given line of phenotype data.

		Adds new strain to an ordered list which is used in make_phenotype_files()
		and make_genotype_files().
		'''
		strain = line[Individual.strain_column_index]
		if strain not in self.strains:
			self.strains[strain] = []
			# set order of strains for use by make_phenotype_files() and make_genotype_files()
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


class Significant_value():
	'''
	Set of functions for working with significant figures in numeric strings

	 Has functions for counting sigfigs, and adding and rounding values
	 '''

	def round(sum, average, rounding_method):
		'''
		Return average that has been rounded

		Use sum and rounding_method to determine appropriate level of precision.

		If the number of sigfigs of of sum is GREATER THAN the sigfigs that
		average has, do nothing. R/QTL will pad average value with
		zeroes so that all values in a column have same precision.

		Using Rounding_method.MAX results in using the rounding rules of
		python's decimal.ROUND_HALF_EVEN:
			Given value xy..., suppose x is a significant digit and y and z are not
			significant.
				ROUND_HALF_EVEN rounds x down
					if y ∈ {0,1,2,3,4}
					else if y == 5
						and x is an even digit (i.e. x ∈ {0,2,4,6,8})
						and all digits after y are 0 or not present at all
				ROUND_HALF_EVEN rounds x up
					if y ∈ {6,7,8,9}
					else if y == 5
						and ( x is an odd digit (i.e. x ∈ {1,3,5,7,9})
						or there exists at least one non-zero digit after y )

		Therefore, for Rounding_method.MAX, the values will be biased towards
		being too high. However, since this MAX keeps more digits than significant
		anyway, it is unlikely for the true value to be affected significantly.

		Arguments:
		sum -- Decimal value
		average -- Decimal value
		rounding_method -- one of Rounding_method values
		'''
		# access global var. rounding_method set by user
		average_rounded = average  # default is to do no rounding
		if Rounding_method.MAX is rounding_method:
			num_sigfigs = Significant_value.num_significant_digits(str(sum))
			setcontext(Context(prec=num_sigfigs, rounding=ROUND_HALF_EVEN))
			average_rounded = +average
		return(average_rounded)

	def sum(values):
		'''
		Sum up list of numeric strings. Return Decimal value.

		Arguments:
		values -- list of strings
		'''

		# context set globally for all Decimal arithmetic, not just for this instance of method
		setcontext( Context( prec=None, rounding=None ) )
		# used in calculation of average and when rounding_method is round.max
		sum = Decimal('0')
		for value in values:
			sum += Decimal(value)
		return(sum)

	def num_significant_digits(value):
		'''
		Counts number of significant figures in a numeric string.
		'''
		parsed_value = Significant_value.get_significant_digits(value)
		parsed_value = Significant_value.remove_decimal_point(parsed_value)
		return( len( parsed_value ) )

	def get_significant_digits(value):
		'''Remove non digits, undesired zeroes, scientific notation characters,
		but leave the decimal point.
			e.g. -034.5E+3 -> 34.5    and   0.004 -> .4'''
		parsed_value = Significant_value.remove_non_digits(value)
		parsed_value = Significant_value.remove_leading_zeroes(parsed_value)
		parsed_value = Significant_value.remove_decimal_placeholding_zeroes(parsed_value)
		return( parsed_value )

	def remove_decimal_point(value):
		return( re.sub(r'\.', r'', value) )

	def remove_non_digits(value):
		'''Remove scientific notation characters and the following symbol(s): -
			-03.05E+4 -> 03.05'''
		regex = r'''
			^					# START from beginning of string
			-?					# remove any negation
			((\d+\.?\d*)		# keep digits
			| (\d*\.\d+))		# (which may or may not be significant)
			.*					# remove any characters after the last digit
			$'''				# STOP at end of sting
		return( re.sub(regex, r'\1', value, flags=re.VERBOSE) )

	def remove_leading_zeroes(value):
		'''Remove leading zeroes only to left of decimal point
		e.g. -03.05E+4 -> 305E+4    and    05 -> 5    and   0.4 -> .4
		and   00 -> 0   and   0.0 -> .0   but   0. -> 0.'''
		regex = r'''
			^					# START from beginning of string
			(-?)				# keep negation
			0*					# reomve as many integral zeroes as possible
			(0					# keep 1 zero if value is a pure integral zero
			| ([1-9]\.?\d*.*)	# OR keep everything beginning with first non-zero integers
		 	| (\.\d+.*))		# OR keep decimal values
			$'''				# STOP at end of sting
		return( re.sub(regex, r'\1\2', value, flags=re.VERBOSE) )

	def remove_decimal_placeholding_zeroes(value):
		'''If value < |1|, remove leading zeroes to left of decimal point,
		plus any zeroes immediately to the right of decimal point that serve
		only as placeholders
		e.g. .05 -> .5    and   0.01 -> .1   and  0.0 -> .0   and  .02E4 -> .2E4'''
		regex = r'''
			^					# START from beginning of string
			(-?)				# keep negation
			0*					# remove any zeroes to left of decimal point
			(\.)				# keep decimal point
			0*					# remove zeroes immediately to right of decimal point
			(\d+				# keeping at least 1 digit, keep at most 1 zero
			.*)					# keep non-digit characters
			$'''				# STOP at end of sting
		return( re.sub(regex, r'\1\2\3', value, flags=re.VERBOSE) )

	def remove_integral_placeholding_zeroes(value):
		'''If value has no decimal point and/or value is not given in
		(quasi) scientific notation, remove trailing zeroes to right of integer
		e.g. 100 -> 1
		but   100. -> 100.   and   2.20E3 -> 2.20E3   and   220E3 -> 220E3'''
		regex = r'''
			^					# START from beginning of string
			(-?)				# keep negation
			([1-9]+)			# keep non-zero digits
			0*					# remove placeholding zeroes
			$'''				# STOP at end of sting
		return( re.sub(regex, r'\1\2', value, flags=re.VERBOSE) )


def sanitize_list(string_list):
	'''Iterates over a list of strings, sanitizing each in turn'''
	for index, string in enumerate(string_list):
		string_list[index] = sanitize(string)
	return(string_list)


def sort_markers( markers_raw, connection ):
	'''Query database for correct order of markers, according to bp position'''

	# query for correct order of markers
	query_for_marker_order = 'SELECT ' + Parameter.MARKER_IDENTIFIER_COLUMN_NAME +\
						  ' FROM ' + Parameter.MARKER_ORDER_SOURCE_TABLE +\
						  Parameter.MARKER_QUALITY_CONDITION +\
						  ' ORDER BY ' +  Parameter.MARKER_CHROMOSOME_COLUMN_NAME +','+  Parameter.BP_POSITION_COLUMN_NAME

	ordering = connection.execute(query_for_marker_order)

	# build list of ordered markers
	markers_ordered = []
	for row in ordering:
		marker = Global.EMPTY_STRING.join(map(str,row))
		# filter sorted markers to just the ones specified in markers input file
		if marker in markers_raw:
			markers_ordered.append(marker)
			markers_raw.pop(marker)		# ensure that each Parameter.MARKER_IDENTIFIER_COLUMN_NAME is unique/included only once
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


def make_genotype_files( data_by_strain, markers_raw, geno_fn_template ):
	'''Main function for building genotype file(s)'''
	num_markers = len(markers_raw)

	# create dictionary holding <file name>:<Geno_file_builder object> pairs
	files = {}

	filenames = [Parameter.MAIN_GENO_FILENAME_PREFIX]
	# open files for writing
	if Global.MAKE_CHROMOSOME_FILES:
		filenames = filenames + Global.CHROMOSOMES

	# for main geno file and (if Global.MAKE_CHROMOSOME_FILES = True) also chromosome files
	for filename in filenames:
		files[filename] = Geno_file_builder(filename, geno_fn_template, data_by_strain)
		files[filename].open()

	# connect to database
	connection = pyodbc.connect(SERVER=Parameter.SQL_SERVER_NAME
		,DATABASE=Parameter.DATABASE
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
		max_rows_to_get = next_row_to_get + Global.QUERY_BATCH_SIZE
		if max_rows_to_get > num_markers:
			max_rows_to_get = num_markers

		# format subset of markers for query's where-clause.
			# Format: markers =   "marker = 'marker_1' or marker = 'marker_2' or...marker = 'marker_n'"
		markers = Parameter.MARKER_IDENTIFIER_COLUMN_NAME + ' = \'' + ('\' or ' + Parameter.MARKER_IDENTIFIER_COLUMN_NAME + ' = \'').join(
			marker for marker in markers_ordered[next_row_to_get:max_rows_to_get]) + '\''

		query_for_genotype_data = ('SELECT ' + Parameter.MARKER_IDENTIFIER_COLUMN_NAME +' as id,'+
				Parameter.MARKER_CHROMOSOME_COLUMN_NAME +','+  Parameter.CENTIMORGAN_COLUMN_NAME +','+ ordered_strains_formatted +
				' FROM ' + Parameter.GENOTYPE_SOURCE_TABLE +
				' WHERE ' + markers +
				' ORDER BY ' +  Parameter.MARKER_CHROMOSOME_COLUMN_NAME +','+  Parameter.CENTIMORGAN_COLUMN_NAME)
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
			geno_file_builders_to_alter = [ files[Parameter.MAIN_GENO_FILENAME_PREFIX] ]

			chromosome = None
			if Global.MAKE_CHROMOSOME_FILES == True:
				# each marker's chromosome name is in column 1 of each row
				chromosome = files[row[1].lower()]
				geno_file_builders_to_alter.append(chromosome)

			# write linebuffer to file if linebuffer is full
			Geno_file_builder.formatted_row = None
			for geno_file_builder in geno_file_builders_to_alter:
				geno_file_builder.append(row)
				if len(geno_file_builder.linebuffer) == Global.MAX_BUFFER_SIZE:
					geno_file_builder.write_linebuffer()

		# write remaining lines if buffers full or query-processing is done
		for geno_file_builder in files.values():
			if max_rows_to_get == num_markers or len(geno_file_builder.linebuffer) == Global.MAX_BUFFER_SIZE:
				geno_file_builder.write_linebuffer()

		next_row_to_get = max_rows_to_get

	# close all files
	for geno_file_builder in files.values():
		geno_file_builder.file.close()

	connection.close()


def make_phenotype_files( lines, pheno_fn_template, use_average_by_strain ):
	'''Main function for building phenotype files'''
	Individual.row_names = (sanitize_list(lines[0][Individual.first_phenotype_column_index: ] +
						[Global.RQTL_SEX_LABEL] + [Global.RQTL_ID_LABEL]) )

	# determines if data will be read in and grouped by strain or kept separated by individual
	data_by_strain = Strains(use_average_by_strain)
	# store iid, sex, strain, and phenotype values for each strain in its own object
	for line in lines[1: ]:
		data_by_strain.append(line)	# also for expanding strain in make_genotype_files()

	# open files for writing:
	phenotype_list_builder = Pheno_file_builder('phenotypes', 'list.txt')
	phenotype_list_builder.open()	# file w/ just the list of sanitized phenotypes
	sexes = [Global.FEMALE, Global.MALE, Global.HETERO]
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
					# append row_name prior to appending first individual's data
					if pheno_file_builder.row == []:
						pheno_file_builder.row.append(row_name)
					'''row_value is a single value for non-averaged inidividual
					and a list of not-yet-averaged values for to-be-averaged individual'''
					row_value = individual.rows[row_index]
					write_row_value = ( pheno_file_builder.do_sexes_match(individual)
						or row_name in Individual.special_rows
						and not row_value ==  Global.RQTL_MISSING_VALUE_LABEL )
					if ( write_row_value ):
						if use_average_by_strain and row_name not in Individual_averaged.special_rows:
							# pass list of not-yet-averaged phenotype values
							pheno_file_builder.row.append(Individual_averaged.average(row_value))
						else:
							pheno_file_builder.row.append(row_value)
					else:
						# write empty string
						pheno_file_builder.row.append( Global.RQTL_MISSING_VALUE_LABEL)
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
		Global.output_dir = sys.argv[3]
		if( not os.path.isdir(Global.output_dir) ):
			os.mkdir(Global.output_dir)

		# Process input for pheno file:
		pheno_input_path = os.path.normpath( sys.argv[1] )
		pheno_file = open(pheno_input_path)

		use_average_by_strain = False
		if num_args == 5 and sys.argv[4] == '-average':
			use_average_by_strain = True

		pheno_lines = [line.strip().split(',') for line in pheno_file]
		print(pheno_lines)
		t0 = time.clock()	# see how long query took
		# Build phenotype files
		phenotype_data_by_strain = make_phenotype_files( pheno_lines, Parameter.PHENO_FILENAME_SUFFIX, use_average_by_strain )
		print( 'Pheno files built in %.2f minutes' % ((time.clock()-t0)/60) )

		# Process input for geno file(s):
		geno_input_path = os.path.normpath( sys.argv[2] )
		geno_file = open(geno_input_path)

		geno_lines = [line.strip().split('\t') for line in geno_file if line.strip()]
		geno_file.close()

		# Convert marker lines to strings, store in dictionary for fast lookup:
		markers = {}
		for line in geno_lines:
			markers[Global.EMPTY_STRING.join(line)] = None

		t0 = time.clock()	# see how long query took
		# Build genotype file(s)
		make_genotype_files( phenotype_data_by_strain, markers, Parameter.GENO_FILENAME_SUFFIX )
		print( 'Geno file built in %.2f minutes' % ((time.clock()-t0)/60) )
