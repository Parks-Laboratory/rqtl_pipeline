## Synopsis
Batch mapping on UW-Madison Condor HTC cluster is accomplished by pre-computing 

## Usage
1. Execute [**run_pipeline.cmd**](../README.md) (with condition set so .rdata file is generated) if not previously executed
2. [**Compile R for portable use**] (build_R/README.md) on CHTC cluster machines, if not done previously
3. Copy the following to the Cluster submit server:
	* **rqtl_inputs.rdata**
	* **map.r**
	* **map.sub**
	* **map.sh**
	* **R.tar.gz**	(portable R installation)


## Summary of important files:
* [**map.r**] (README_MAP.R.md)
  * Perform mapping, create graphs and generated data

* map.sh
  * Instrucions for each node of cluster

* map.sub
  * Instructions for CHTC submit server

* mkdirs.sh
  * Sets up hierarchy of directories on submit server to store generated output files

