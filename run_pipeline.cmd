SETLOCAL

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Temporarily add locations to the search path
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: specifiy location of rqtl_pipeline
	PATH %PATH%;E:\rqtl_pipeline\

	:: specify location of file with list of strains


cls

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Filter SNPs with PLINK
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	:: build input files for PLINK
	get_plink.py strains.txt
	:: run PLINK
	SET tempDir=%RANDOM%
	md tempDir
	plink1 --tfile strains --make-bed --geno 0.1 --maf 0.05 --out 1.07/strains_1.07 --write-snplist

	:: clean up
	rm

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Make input files for R/QTL
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
