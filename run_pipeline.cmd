SETLOCAL

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Temporarily add locations to the search path
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: specifiy location of rqtl_pipeline
	PATH %PATH%;E:\rqtl_pipeline\

	:: check that all requirements are installed

	:: specify location of file with phenotype data
	SET PHENOTYPE_FILE=?

	:: specify location for all R/QTL input files, PLINK input/output files
	SET OUTPUT_DIR=?

	:: R/QTL-related
	SET USE_AVERAGE_BY_STRAIN=True

	cls

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Extract strains and phenotypes from PHENOTYPE_FILE
::		& Make phenotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: run make_rqtl_inputs.make_phenotype_files() to build:
		:: phenotype file (for R/QTL mapping)
		:: strains_list.txt (for make_plink_inputs.py)
		:: phenotypes_list.txt (for batch R/QTL mapping)

	make_rqtl_inputs -out %OUTPUT_DIR% -pheno %PHENOTYPE_FILE% -avg %USE_AVERAGE_BY_STRAIN%


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Filter SNPs with PLINK
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	SET "SERVER= PARKSLAB"
	SET "DATABASE= HMDP"
	SET "PLINK_GENOTYPE_VIEW= [dbo].[genotype_calls_plink_format]"
	SET "MARKER_IDENTIFIER_COLUMN_NAME= rsID"
	SET "MARKER_CHROMOSOME_COLUMN_NAME= snp_chr"
	SET "BP_POSITION_COLUMN_NAME= snp_bp_mm10"

	:: build input files for PLINK
	make_plink_inputs.py -strains strains_list.txt %PLINK_GENOTYPE_VIEW%

	:: run PLINK
	plink1 --tfile strains --make-bed --geno 0.1 --maf 0.05 --out %OUTPUT_DIR% --write-snplist


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make genotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	SET "SERVER= PARKSLAB"
	SET "DATABASE= HMDP"
	SET "RQTL_GENOTYPE_VIEW = [dbo].[rqtl_csvsr_geno_format]"
	SET "MARKER_IDENTIFIER_COLUMN_NAME= rsID"
	SET "MARKER_CHROMOSOME_COLUMN_NAME= snp_chr"
	SET "BP_POSITION_COLUMN_NAME= snp_bp_mm10"
	SET "CENTIMORGAN_COLUMN_NAME= cM_est_mm10"
	SET "MARKER_QUALITY_CONDITION=  WHERE flagged = 0 and quality = good"

	make_rqtl_inputs -out %OUTPUT_DIR% -pickle %STRAINS.pkl% -view %RQTL_GENOTYPE_VIEW%
