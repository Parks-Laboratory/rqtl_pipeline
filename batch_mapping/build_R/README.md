## Synopsis
Compiles a portable version of the R statistical package plus optional additional R packages for use on UW-Madison Condor HTC cluster.

## Usage
1. Copy these files to the Condor submit server
	* **install_r.sh** 
	* **install_r.sub**
	* **R-*X.X.X.*tar.gz**  (where *X.X.X* is the version of R, which must match what is written in **install_r.sh** and **install_r.sub**
	* **install_packages.R**
	
	`scp install_r.sh install_r.sub R-X.X.X.tar.gz install_packages.R username@submit-3.chtc.wisc.edu`

2. SSH into the submit server

	`ssh username@submit-3.chtc.wisc.edu`

3. Submit the job (puts user in interactive session)

	`condor_submit -i install_r.sub`
	
4. Execute the script to do the compilation, wait for it to finish (may take several minutes), then exit the session. Compiled version stored in a file **R.tar.gz** on submit server.
	
	```
	$ ./install_r.sh
	:
	$ exit
	```
	

