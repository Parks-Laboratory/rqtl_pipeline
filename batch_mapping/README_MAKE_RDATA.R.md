## Synopsis: 
Does pre-processing using R/QTL to prevent duplicate work on each node of cluster. A minimal amount of data is then packaged up as an .rdata file which can then be sent along to the nodes.

## Usage: 
Open Windows command line in directory containing input files, and do

   ```R CMD BATCH --no-save make_rdata.r```

## Inputs:

* Produced by make_rqtl_inputs.py:
  * main_csvsr_geno.csv
  * female_csvsr_pheno.csv
  * male_csvsr_pheno.csv
  * hetero_csvsr_pheno.csv
    * (still required, but not used)
  * phenotypes_list.txt
    * indexed into by each node of cluster to ensure that duplicate work is not done
