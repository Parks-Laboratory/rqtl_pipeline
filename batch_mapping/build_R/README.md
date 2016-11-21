## Synopsis
Compiles a portable version of the R statistical package plus optional additional R packages for use on UW-Madison Condor HTC cluster.

## Usage
1. Copy all of these files to the Condor submit server:
	* **install_r.sh** 
	* **install_r.sub**
	* **R-*X.X.X.*tar.gz**  (where *X.X.X* is the version of R, which must match what is written in **install_r.sh** and **install_r.sub**
	* **install_packages.R**
2. Submit job
	
	`condor_submit install_r.sub`
