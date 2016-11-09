::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Instructions for running script
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: 1) make copy of this script (and make_rdata.r if doing batch mapping)
	::		and set parameters in this script
	:: 2) run this script in directory containing:
	::		csv file with strains in rows and traits in columns
	::		make_rdata.r (if doing batch mapping)
	:: 3) script creates directory (specified by OUTPUT_DIR below)
	::		in which all generated files are placed



::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Temporarily add locations to the search path
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	SETLOCAL

	:: batch or interactive mapping?
	:: (must make local copy of make_rdata.r and edit the mapping jobs)
	SET BATCH_MAPPING=%TRUE%`

	:: specifiy location of rqtl_pipeline directory
	SET %rqtl_pipeline%=E:\rqtl_pipeline\



	:: add script locations to Windows' PATH variable, so cmd.exe can find them
	PATH %PATH%;%rqtl_pipeline%;%rqtl_pipeline%\filter_markers;%rqtl_pipeline%\make_rqtl_inputs;%rqtl_pipeline%\make_rqtl_inputs\src

	:: check that all requirements are installed

	:: specify location for all R/QTL input files, PLINK input/output files
	SET "OUTPUT_DIR=rqtl_%RANDOM%"

	SET TRUE=0==0
	SET FALSE=NOT %TRUE%

	cls


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Extract strains and phenotypes from PHENOTYPE_FILE
::		& Make phenotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: Inputs:
		:: csv file with strains in rows and traits in columns
	:: Outputs:
		:: phenotype file (for R/QTL mapping)
		:: strains_list.txt (for make_plink_inputs.py)
		:: phenotypes_list.txt (for batch R/QTL mapping)

	make_rqtl_inputs.py -out %OUTPUT_DIR% pheno -phenoFile bxd.csv -avg


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Filter SNPs with PLINK
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: build input files for PLINK

	make_plink_inputs.py -strains %OUTPUT_DIR%/strains_list.txt -db HMDP -table [dbo].[genotype_calls_plink_format] -out %OUTPUT_DIR% -idCol rsID -chrCol snp_chr -posCol snp_bp_mm10


	:: run PLINK ()
	::		To output just the list of SNPs that remain after all filtering,
	::		etc, use the --write-snplist command, e.g. to get a list of all
	::		high frequency, high genotyping-rate SNPs:
	:: 			plink --bfile mydata --maf 0.05 --geno 0.05 --write-snplist

	plink --tfile %OUTPUT_DIR%/plink_input --make-bed --geno 0.1 --maf 0.05 --out %OUTPUT_DIR%/filtered_markers --write-snplist


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make genotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	make_rqtl_inputs.py -out %OUTPUT_DIR% geno -table "[dbo].[rqtl_csvsr_geno_format]" -mkTable "[dbo].[genotypes]" -db HMDP -mkFile %OUTPUT_DIR%/filtered_markers.snplist



::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make inputs for R/QTL Batch Mapping
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: Perform these actions if BATCH_MAPPING is True
	IF %BATCH_MAPPING% (
		MOVE make_rdata.r %OUTPUT_DIR%
		cd %OUTPUT_DIR%
		R CMD BATCH --no-save make_rdata.r
		cd ..
	)
