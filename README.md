# R/QTL Mapping Pipeline  (README IN PROGRESS)
## Synopsis


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

## Installation

Provide code examples and explanations of how to get the project.

## Tests

Requirements:<br>
	Python 3.X installed<br>
	Path: 
		C:\Program Files\plink_1.90_win64\

Required non-standard Python Packages:
pyodbc
testfixtures

To install python package from command line do:
pip install <package name>

Procedure for building R/QTL input files:<br>
-Open command-line in directory with input files<br>

(more documentation to come...)
