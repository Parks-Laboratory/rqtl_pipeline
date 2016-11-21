## Synopsis
Batch mapping on UW-Madison Condor HTC cluster is accomplished by pre-computing 

## Usage
1. Execute [**run_pipeline.cmd**](../../) (with condition set so .rdata file is generated) if not previously executed
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

