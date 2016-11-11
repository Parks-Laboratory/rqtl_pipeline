## Synopsis
The R/QTL Mapping Pipeline is a collection of scripts that streamline the process of building input files for Karl Broman's quantitative trait loci analysis package for R. The scripts connect to a database containing genotype data, filter markers using PLINK, and finally use this subset of markers along with some phenotype data to build csvsr-formatted input files for R/QTL.

### Outline
make PLINK inputs  -->  run PLINK  -->  make R/QTL inputs  -->  perform R/QTL mapping

### Summary of primary scripts
* **run_pipeline.cmd**
	* this is the backbone of the pipeline. It makes calls to scripts in the sub-directories and to make_rdata.r
* **make_rdata.r**
	* outputs file for performing mapping on Condor HTC cluster
	* called by run_pipeline.cmd
* filter_markers/[**make_plink_inputs.py**] (make_plink_inputs/README.md)
	* outputs file containing a sub-set of genotyped positions that meet specified conditions 
	(e.g. allele frequency, maximum missing rate)
	* called by run_pipeline.cmd
* make_rqtl_inputs/src/[**make_rqtl_inputs.py**] (make_rqtl_inputs/README.md)
	* outputs files with genotype and phenotype information in the csvsr format specified by R/QTL
	* called by run_pipeline.cmd
	* see make_rqtl_inputs/README for more details
* [**batch_mapping/**] (batch_mapping/README.md)
	* collection of scripts which perform R/QTL mapping on UW-Madison CHTC cluster

## Code Example


Set values all capitalized variables in run_pipeline.cmd, run it from Windows command line
For interactive mapping:

For batch mapping on UW-Madison Cluster:

1. Copy make_rdata.r to the directory with the csvsr R/QTL files.
2. Open make_rdata.r with R/RStudio. Edit variables marked as parameters and edit mapping jobs.
3. Run the script.
4. Follow README in build_R directory if you have not previously compiled R for use on cluster
5. Copy the following to the Cluster submit server:
		rqtl_inputs.rdata, map.r, map.sub, map.sh, R.tar.gz

## Motivation
A short description of the motivation behind the creation and maintenance of the project. This should explain **why** the project exists.

## Requirements
The following programs should be installed and exist in the Windows PATH environment variable
* PLINK 1.9  
	* Available at: https://www.cog-genomics.org/plink2
* Python 3.X  (tested on Python 3.5)  
	* Available at: https://www.python.org/
* R (tested on 3.2.4)
	* Available at: https://cran.r-project.org/


Required Python modules:
* PYODBC

Required Python modules for testing:
* testfixtures (for making temporary directories)

Install python modules from Windows Command Prompt via `python -m pip install SomeModule`

## Tests
* make_rqtl_inputs/test
	* Contains test files for major classes and functions in make_rqtl_inputs.py
