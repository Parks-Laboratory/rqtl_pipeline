## Synopsis
Batch mapping on UW-Madison Condor HTC cluster is accomplished by pre-computing 

## Usage
1. Execute [**run_pipeline.cmd**](../README.md) (with condition set so .rdata file is generated) if not previously executed
2. [**Compile R for portable use**] (build_R/README.md) on CHTC cluster machines, if not done previously
3. Copy the following to the Cluster submit server:
	* **map.sub**
	* **map.sh**
	* **map.r**
	* **rqtl_inputs.rdata**
	* **R.tar.gz**	(portable R installation)
	* **mkdirs.sh**
	
	`scp map.sub map.sh map.r rqtl_inputs.rdata R.tar.gz mkdirs.sh username@submit-3.chtc.wisc.edu`
	
4. SSH into the submit server

	`ssh username@submit-3.chtc.wisc.edu`


3. Submit the job

	`condor_submit map.sub`
	
4. Wait for jobs to finish, copy back 
	
	
## Summary of important files:
* [**map.r**] (README_MAP.R.md)
  * Perform mapping, create graphs and generated data

* map.sh
  * Instrucions for each node of cluster

* map.sub
  * Instructions for CHTC submit server

* mkdirs.sh
  * Sets up hierarchy of directories on submit server to store generated output files

## Requirements:
