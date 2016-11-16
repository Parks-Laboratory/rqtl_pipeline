## Synopsis
Batch mapping on UW-Madison Condor HTC cluster is accomplished by pre-computing 

## Usage
1. Copy make_rdata.r to the directory with the csvsr R/QTL files.
2. Open make_rdata.r with R/RStudio. Edit variables marked as parameters and edit mapping jobs.
3. Run the script.
4. Follow README in build_R directory if you have not previously compiled R for use on cluster
5. Copy the following to the Cluster submit server:
		rqtl_inputs.rdata, map.r, map.sub, map.sh, R.tar.gz


## Summary of important files:
* [**map.r**] (README_MAP.R.md)
  * Perform mapping, create graphs and generated data

* map.sh
  * Instrucions for each node of cluster

* map.sub
  * Instructions for CHTC submit server

* mkdirs.sh
  * Sets up hierarchy of directories on submit server to store generated output files

