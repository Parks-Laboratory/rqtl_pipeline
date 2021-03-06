:: Filters genotype markers using PLINK and builds inputs for R/QTL
:: See README_RUN_PIPELINE.md for more details

:: DON'T CHANGE THIS
SETLOCAL
SET TRUE=0==0
SET FALSE=NOT %TRUE%

:: DON'T CHANGE THIS unless rqtl_pipeline directory is moved
SET rqtl_pipeline=E:\rqtl_pipeline\

:: DON'T CHANGE THIS
	:: add script locations to Windows' PATH variable, so cmd.exe can find them
PATH %PATH%;%rqtl_pipeline%\;%rqtl_pipeline%\filter_markers\;%rqtl_pipeline%\make_rqtl_inputs\;%rqtl_pipeline%\make_rqtl_inputs\src\

:: DON'T CHANGE THIS
	:: specify location for all generated R/QTL input files, PLINK input/output files
SET "OUTPUT_DIR=rqtl_%RANDOM%"

cls


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Extract strains and phenotypes from PHENOTYPE_FILE
::		& Make phenotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: CHANGE THIS
		:: assumes -avg is either used/not used for both R/QTL pheno/geno files
	make_rqtl_inputs.py -out %OUTPUT_DIR% -avg pheno -phenoFile bxd.csv


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Filter SNPs with PLINK
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: CHANGE THIS
		:: assumes that make_rqtl_inputs pheno created file "strains_list.txt"
	make_plink_inputs.py -strains %OUTPUT_DIR%/strains_list.txt -db HMDP -table [dbo].[genotype_calls_plink_format] -out %OUTPUT_DIR%/plink_input -idCol rsID -chrCol snp_chr -posCol snp_bp_mm10


	:: CHANGE THIS
		:: (NOTE: don't change anything that looks like  file/directory name)
		:: file-prefix specified in --tfile must match file-prefix specified
		:: in -out option of make_plink_inputs
	plink --tfile %OUTPUT_DIR%/plink_input --make-bed --geno 0.1 --maf 0.05 --out %OUTPUT_DIR%/filtered_markers --write-snplist


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make genotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: CHANGE THIS
		:: file-prefix specified in -mkFile must match file-prefix specified in --out option of PLINK
		:: assumes -avg is either used/not used for both R/QTL pheno/geno files
	make_rqtl_inputs.py -out %OUTPUT_DIR% -avg geno -mkFile %OUTPUT_DIR%/filtered_markers.snplist -table "[dbo].[rqtl_csvsr_geno_format]" -mkTable "[dbo].[genotypes]" -db HMDP



::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make inputs for R/QTL Batch Mapping
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

	:: CHANGE THIS first line's condition to %TRUE% if you want to generate input file
	:: for mapping on CHTC cluster
	IF %TRUE% (
		:: DON'T CHANGE THIS
		copy make_rdata.r %OUTPUT_DIR%
		copy run_pipeline.cmd %OUTPUT_DIR%
		robocopy %rqtl_pipeline%\batch_mapping %OUTPUT_DIR% map.* mkdirs.sh R.tar.gz
		SET prevDir=%cd%
		cd %OUTPUT_DIR%
		R CMD BATCH --no-save make_rdata.r
		cd %prevDir%
	)
