## Goal
Retrieves Mouse Diversity Array genotypes from database in csvsr R/QTL format

## File formats
The csvsr format has a column for each individual and genotype data or phenotype
(depending on the file) in the rows (see Outputs section below). This file format
was chosen because Microsoft SQL Server tables have a maximum number of columns,
but unlimited number of rows. Individuals could go in either rows or columns,
but the number of markers (and possibly number of phenotypes) will probably be
too many to fit in columns, so must go in rows.

Usage: ```make_rqtl_inputs -h ```to get list of options

Inputs:

	1) File containing the list of markers, one on each line
		File Format:
			<1st marker id>
			<2nd marker id>
			...
			<mth marker id>
	2) CSV containing phenotype data
		File format:
			Mouse ID,id,Sex,<phenotype label 1>,...,<phenotype label n>
			<1st individual id>,<strain id>,<Male/Female>,<1st phenotype>,...,<jth phenotype>
			...
			<ith individual id>,<strain id>,<Male/Female>,<1st phenotype>,...,<jth phenotype>
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
			<Global.RQTL_ID_LABEL>,,,<1st individual's id>,...,<mth individual's id>
			<1st marker id>,<chromosome #>,<centimorgans>,<1st individual's genotype>,...,<ith individual's genotype>
			...
			<mth marker id>,<chromosome #>,<centimorgans>,<1st individual's genotype>,...,<ith individual's genotype>

	Phenotype files:
		Filename format:
			<female pheno filename prefix><Parameter.PHENO_FILENAME_SUFFIX>
				e.g. "female_pheno_csvsr.csv"
			<male pheno filename prefix><Parameter.PHENO_FILENAME_SUFFIX>
				e.g. "male_pheno_csvsr.csv"
			<hetero pheno filename prefix><Parameter.PHENO_FILENAME_SUFFIX>
				e.g. "hetero_pheno_csvsr.csv"
		File format:
			<1st phenotype label>, <1st individual's phenotype>,...,<ith individual's phenotype>
			...
			<jth phenotype label>, <1st individual's phenotype>,...,<ith individual's value>
			<Global.RQTL_SEX_LABEL>,<1st individual's sex>,...,<ith individual's sex>
			<Global.RQTL_ID_LABEL>,<1st individual's id>,...,<ith individual's id>

		Notes:
		* hetero file contains phenotype values for all males and females
		* female file contains phenotype values for all females, and marks
			the phenotype values for all males as missing
		* male file (analogous to female file, female values all marked missing)




Notes:
* make_genotype_files() is dependent on results from make_phenotype_files().
	This is due to the contraint that R/QTL requires the columns of both
	input files to match up (i.e. order of individuals is same in both files)
	
## Tests
[**make_rqtl_inputs/test/**](test/README.md)
* Contains test files for major classes and functions in make_rqtl_inputs.py


## Known issues
* Bug-source must be identified and fixed before MAKE_CHROMOSOME_FILES can
	be enabled. This option is intended to split genotype data into smaller, more
	manageable chunks by creating a file for each chromosome in which only the
	relevant subset of markers would be included.

## Future ideas
* Create temporary table in databse w/ all the markers, using the marker id
	as primary key. Later, use this table in make_genotype_files() query instead of
	the massive WHERE clause which currently has thousands of conditions per query
* May be able to simplifiy script using Pandas Scientific Computing library
* Script can be vastly simplified if phenotype data stored in database
* Re-implement completely:
	* If all phenotype and genotype data are in a database, create a view
		and just pull from that.
		* PRO(s): The benefit is that this script wouldn't need to provide functionality
		already implemented by the database engine (significantly, pivot function).
		* CON(s): This forces the user to first import all data to database
		(which will force user to clean up their data and titles first).
* Are separate files really needed for male/female phenos? Can R/QTL do scanning
	with only one sex at a time when given both sexes?
