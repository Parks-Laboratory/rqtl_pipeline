:: Filters genotype markers using PLINK and builds inputs for R/QTL
:: See README.md for more details


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Temporarily add locations to the search path
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	SETLOCAL
	SET TRUE=0==0
	SET FALSE=NOT %TRUE%

	:: batch or interactive mapping?
	:: (must make local copy of make_rdata.r and edit the mapping jobs)
	:: (NOTE: may need to change this)
	SET BATCH_MAPPING=%TRUE%

	:: specifiy location of rqtl_pipeline directory (NOTE: may need to change this)
	SET %rqtl_pipeline%=E:\rqtl_pipeline\

	:: add script locations to Windows' PATH variable, so cmd.exe can find them
	PATH %PATH%;%rqtl_pipeline%;%rqtl_pipeline%\filter_markers;%rqtl_pipeline%\make_rqtl_inputs;%rqtl_pipeline%\make_rqtl_inputs\src

	:: specify location for all R/QTL input files, PLINK input/output files
	SET "OUTPUT_DIR=rqtl_%RANDOM%"


	cls


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Extract strains and phenotypes from PHENOTYPE_FILE
::		& Make phenotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: (NOTE: may need to change parameters)
	:: Run this command for description of parameters:
	::		make_rqtl_inputs.py pheno -h
	make_rqtl_inputs.py -out %OUTPUT_DIR% pheno -phenoFile bxd.csv -avg


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Filter SNPs with PLINK
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: build input files for PLINK
		:: (NOTE: may need to change parameters)
		:: Run this command for description of parameters:
		::		make_plink_inputs.py -h
	make_plink_inputs.py -strains %OUTPUT_DIR%/strains_list.txt -db HMDP -table [dbo].[genotype_calls_plink_format] -out %OUTPUT_DIR% -idCol rsID -chrCol snp_chr -posCol snp_bp_mm10


	:: run PLINK ()
		::	To output just the list of SNPs that remain after all filtering,
		::	etc, use the --write-snplist command, e.g. to get a list of all
		::	high frequency, high genotyping-rate SNPs:
		::		plink --bfile mydata --maf 0.05 --geno 0.05 --write-snplist
		:: See https://www.cog-genomics.org/plink2 for description of parameters
	plink --tfile %OUTPUT_DIR%/plink_input --make-bed --geno 0.1 --maf 0.05 --out %OUTPUT_DIR%/filtered_markers --write-snplist


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make genotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: Run this command for description of parameters:
	::		make_rqtl_inputs.py geno -h
	make_rqtl_inputs.py -out %OUTPUT_DIR% geno -table "[dbo].[rqtl_csvsr_geno_format]" -mkTable "[dbo].[genotypes]" -db HMDP -mkFile %OUTPUT_DIR%/filtered_markers.snplist -avg



::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make inputs for R/QTL Batch Mapping
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: Perform these actions if BATCH_MAPPING is True  (NOTE: nothing to change here)
	IF %BATCH_MAPPING% (
		MOVE make_rdata.r %OUTPUT_DIR%
		cd %OUTPUT_DIR%
		R CMD BATCH --no-save make_rdata.r
		cd ..
	)
