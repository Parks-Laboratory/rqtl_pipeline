## Synopsis
Batch mapping on UW-Madison Condor HTC cluster is accomplished by using pre-computed R/QTL objects (stored in an .rdata file) and using the unique process ID to index into a list of traits and mapping jobs. Each node of the cluster performs analysis for a unique trait/mapping job pair (e.g. mapping insulin for males). See this [introduction to running Condor jobs] (http://chtc.cs.wisc.edu/helloworld.shtml) for a primer.

## Usage
0. Execute [**run_pipeline.cmd**](../README.md) (with condition set so .rdata file is generated) if not previously executed
0. [**Compile R for portable use**] (build_R/README.md) on CHTC cluster machines, if not done previously
0. Modify the number of jobs to queue by editing the number after 'queue' in **map.sub**. For each phenotype in the input phenotype file, there is one job for each of the mapping_jobs in make_rdata.r, so the number to use here is:
	
		(number of mapping jobs in make_rdata.r) x (number of traits in input phenotype file)
0. (Optional) In **map.sh** on line beginning with "R CMD BATCH", 
	* set `plot='TRUE'` to generate a plot of lods and save as pdf
	* set `summary='TRUE'` to generate .log file with highest lod per chromosome
	* set `rdata='TRUE'` to generate .rdata file with output of R/QTL scan (use to generate more plots from existing scan)
	* set `scan_algo='hk'` or `scan_algo='em'` to specify the algorithm R/QTL will use to calculate LOD values
	* set `calculate_thresholds='TRUE` to calculate significance LOD thresholds

0. Copy the following to the Cluster submit server:
	* **map.sub**
	* **map.sh**
	* **map.r**
	* **rqtl_inputs.rdata**
	* **R.tar.gz**	(portable R installation)
	* **mkdirs.sh**
	
	`$ scp map.sub map.sh map.r rqtl_inputs.rdata R.tar.gz mkdirs.sh username@submit-3.chtc.wisc.edu:`
	
0. SSH into the submit server

	`$ ssh username@submit-3.chtc.wisc.edu`

0. Create directories `runs` and `runs/_logs`

	`$ ./mkdirs.sh`


0. Submit the job

	`$ condor_submit map.sub`
	
0. Wait for jobs to finish, exit the session, and copy back the results directory

	```
	$ exit
	$ scp -r username@submit-3.chtc.wisc.edu:runs .
	```
	
	
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
* Program capable of making an SSH connection (e.g. Cygwin, PuTTY)
