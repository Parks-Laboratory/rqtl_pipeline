## Important paramters
### To get descriptions of parameters:
* `make_plink_inputs.py -h`
* `make_rqtl_inputs.py pheno -h`
* `make_rqtl_inputs.py geno -h`
* `plink -h`
	
### For make_rqtl_inputs:
* -avg
	* averages all male phenotypes of a strain and all female phenotypes of a strain (both geno and pheno files affected)
	* either do:
		* `make_rqtl_inputs.py -avg pheno ...` and `make_rqtl_inputs.py -avg geno ...`, or
		* `make_rqtl_inputs.py pheno ...` and `make_rqtl_inputs.py geno ...`
