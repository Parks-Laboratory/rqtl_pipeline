:: Filters genotype markers using PLINK and builds inputs for R/QTL
:: See README_RUN_PIPELINE.md for more details


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Temporarily add locations to the search path
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: DON'T CHANGE THIS
	SETLOCAL
	SET TRUE=0==0
	SET FALSE=NOT %TRUE%

	:: DON'T CHANGE THIS unless rqtl_pipeline directory is moved
	SET %rqtl_pipeline%=E:\rqtl_pipeline\

	:: DON'T CHANGE THIS
		:: add script locations to Windows' PATH variable, so cmd.exe can find them
	PATH %PATH%;%rqtl_pipeline%;%rqtl_pipeline%\filter_markers;%rqtl_pipeline%\make_rqtl_inputs;%rqtl_pipeline%\make_rqtl_inputs\src

	:: DON'T CHANGE THIS
		:: specify location for all generated R/QTL input files, PLINK input/output files
	SET "OUTPUT_DIR=rqtl_%RANDOM%"

	cls


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Extract strains and phenotypes from PHENOTYPE_FILE
::		& Make phenotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: CHANGE THIS
	make_rqtl_inputs.py -out %OUTPUT_DIR% -avg pheno -phenoFile bxd.csv


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Filter SNPs with PLINK
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: CHANGE THIS
		:: assumes that make_rqtl_inputs pheno created file "strains_list.txt"
	make_plink_inputs.py -strains %OUTPUT_DIR%/strains_list.txt -db HMDP -table [dbo].[genotype_calls_plink_format] -out %OUTPUT_DIR%/plink_input -idCol rsID -chrCol snp_chr -posCol snp_bp_mm10


	:: CHANGE THIS
		:: (NOTE: don't change anything that looks like  file/directory name)
	plink --tfile %OUTPUT_DIR%/plink_input --make-bed --geno 0.1 --maf 0.05 --out %OUTPUT_DIR%/filtered_markers --write-snplist


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make genotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: CHANGE THIS
		:: file-prefix specified in -mkFile must match file-prefix specified in --out option of PLINK
	make_rqtl_inputs.py -out %OUTPUT_DIR% -avg geno -mkFile %OUTPUT_DIR%/filtered_markers.snplist -table "[dbo].[rqtl_csvsr_geno_format]" -mkTable "[dbo].[genotypes]" -db HMDP



::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make inputs for R/QTL Batch Mapping
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: CHANGE THIS to TRUE if you want to map on CHTC cluster

	:: DON'T CHANGE THIS
	IF %TRUE% (
		MOVE make_rdata.r %OUTPUT_DIR%
		SET prevDir=%cd%
		cd %OUTPUT_DIR%
		R CMD BATCH --no-save make_rdata.r
		cd %prevDir%
	)
