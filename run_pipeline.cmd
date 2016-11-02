SETLOCAL

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Temporarily add locations to the search path
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: specifiy location of rqtl_pipeline
	PATH %PATH%;E:\rqtl_pipeline\;E:\rqtl_pipeline\filter_markers;E:\rqtl_pipeline\make_rqtl_inputs;E:\rqtl_pipeline\make_rqtl_inputs\src

	:: check that all requirements are installed

	:: specify location for all R/QTL input files, PLINK input/output files
	SET OUTPUT_DIR=?

	:: R/QTL-related


	:: batch or interactive mapping?
	:: (must make local copy of make_rdata.r and edit the mapping jobs)
	SET BATCH_MAPPING=?

	cls

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Extract strains and phenotypes from PHENOTYPE_FILE
::		& Make phenotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: Outputs:
		:: phenotype file (for R/QTL mapping)
		:: strains_list.txt (for make_plink_inputs.py)
		:: phenotypes_list.txt (for batch R/QTL mapping)

	make_rqtl_inputs -out %OUTPUT_DIR% -phenoFile name.csv -avg


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Filter SNPs with PLINK
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: build input files for PLINK
	make_plink_inputs.py -strains strains.txt -db HMDP -table [dbo].[genotype_calls_plink_format] -idCol rsID -chrCol snp_chr -posCol snp_bp_mm10

	:: run PLINK
	plink1 --tfile strains --make-bed --geno 0.1 --maf 0.05 --out %OUTPUT_DIR% --write-snplist


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make genotype file for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	make_rqtl_inputs -out %OUTPUT_DIR% -pickle %STRAINS.pkl% -view %RQTL_GENOTYPE_VIEW%



::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make inputs for R/QTL Batch Mapping
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: Perform these actions if BATCH_MAPPING is True

	:: Build rdata file using R CMD Batch
