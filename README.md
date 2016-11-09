## Synopsis
The R/QTL Mapping Pipeline is a collection of scripts that streamline the process of building input files for Karl Broman's quantitative trait loci analysis package for R. The scripts connect to a database containing genotype data, filter markers using PLINK, and finally use this subset of markers along with some phenotype data to build csvsr-formatted input files for R/QTL.

### Explanation of sub-directories and important files

At the top of the file there should be a short introduction and/ or overview that explains **what** the project is.

## Code Example


Set values all capitalized variables in run_pipeline.cmd, run it from Windows command line
For interactive mapping:

For batch mapping on UW-Madison Cluster:
	Copy make_rdata.r to the directory with the csvsr R/QTL files.
	Open make_rdata.r with R/RStudio. Edit variables marked as parameters and edit mapping jobs.
	Run the script.
	Follow README in build_R directory if you have not previously compiled R for use on cluster
	Copy the following to the Cluster submit server:
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

Procedure for building R/QTL input files:<br>
-Open command-line in directory with input files<br>

(more documentation to come...)
