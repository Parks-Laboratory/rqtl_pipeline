## Code Examples
* Get descriptions of parameters:
	* `make_plink_inputs.py -h`
	* `make_rqtl_inputs.py pheno -h`
	* `make_rqtl_inputs.py geno -h`
	* `plink -h`


## PLINK 
Useful parameters:
> --geno *{maximum per-variant}*
>* filters out all variants with missing call rates exceeding the provided value (default 0.1) to be removed

> --maf *minimum freq*
>* filters out all variants with minor allele frequency below the provided threshold (default 0.01)

> --write-snplist
> writes *.sniplist file containing only the SNPs that remain after filtering
* e.g. to get a list of all high frequency, high genotyping-rate SNPs:
	* `plink --bfile mydata --maf 0.05 --geno 0.05 --write-snplist`

(from https://www.cog-genomics.org/plink2/filter)
