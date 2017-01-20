## Synopsis
The R/QTL Mapping Pipeline is a collection of scripts that streamline the process of building input files for Karl Broman's quantitative trait loci analysis package for R. The scripts connect to a database containing genotype data, filter markers using PLINK, and finally use this subset of markers along with some phenotype data to build csvsr-formatted input files for R/QTL.

## Outline
make PLINK inputs  -->  run PLINK  -->  make R/QTL inputs  -->  perform R/QTL mapping

## Usage
1. place a copy of **run_pipeline.cmd** in directory containing	[**file with phenotype data**](make_rqtl_inputs/README.md#pheno)
2. set parameters in **run_pipeline.cmd**
3. (Optional) if doing batch mapping with UW-Madison's Condor HTC cluster, place a copy of **make_rdata.r** in same directory as **run_pipeline.cmd** and specify what mapping jobs to do in **make_rdata.r** (see comments in **make_rdata.r** for details on specifying mapping jobs and [**map.r**](batch_mapping/README_MAP.R.md#mapping-theory) for general mapping information.) 
4. execute run_pipeline.cmd in Windows Command Prompt\* by simply typing 

		run_pipeline.cmd

	\* Note: Shift+Right-click inside a directory in File Explorer and select "Open command window here" to start Windows Command Prompt in current directory
	
For interactive mapping:

1. open interactive_mapping/[**rqtl_mapping.r**] (interactive_mapping/README.md) with [RStudio](https://www.rstudio.com/) or [RGui](https://cran.r-project.org/)
2. after loading data into a cross object, choose blocks of code to run

For batch mapping on UW-Madison Cluster:

1. see [documentation](batch_mapping/README.md)


## Summary of primary scripts
* [**run_pipeline.cmd**](README_RUN_PIPELINE.md)
	* this is the backbone of the pipeline. It makes calls to scripts in the sub-directories and to make_rdata.r
	* produces directory in which all generated files (including files for R/QTL mapping) are placed
* **make_rdata.r**
	* outputs file for performing mapping on Condor HTC cluster
	* called by run_pipeline.cmd
* filter_markers/**make_plink_inputs.py**
	* outputs input files for PLINK which can then filter markers down to a sub-set that meet specified conditions 
	(e.g. allele frequency, maximum missing rate)
	* called by run_pipeline.cmd
* make_rqtl_inputs/src/[**make_rqtl_inputs.py**] (make_rqtl_inputs/README.md)
	* outputs files with genotype and phenotype information in the csvsr format specified by R/QTL
	* called by run_pipeline.cmd
* [**batch_mapping/***] (batch_mapping/README.md)
	* collection of scripts which perform R/QTL mapping on UW-Madison CHTC cluster
* interactive_mapping/[**rqtl_mapping.r**] (interactive_mapping/README.md)
	* R script with commonly used mapping commands, for use in R interactive session

## Requirements
The following programs should be installed and exist in the Windows PATH environment variable
* [PLINK 1.9] (https://www.cog-genomics.org/plink2)
* [Python 3.X] (https://www.python.org/)  (tested on Python 3.5)  
* [R] (https://cran.r-project.org/) (tested on 3.2.4)


Required Python modules:
* [PYODBC] (https://mkleehammer.github.io/pyodbc/)

Install python modules from Windows Command Prompt via:
	
	python -m pip install SomeModule
