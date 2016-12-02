#!/bin/bash

# Given a list of traits, run a subset of them
# (m,f,covariate (additive, interactive)), (logged/not-logged)

# set up working environment
tar -xzf R.tar.gz

# make sure the script will use your R installation
export PATH=$(pwd)/R/bin:$PATH

R CMD BATCH --slave "--args chtc_process_number='$1' rdata_file='rqtl_inputs.rdata' plot='FALSE' summary='FALSE' rdata='FALSE' scan_algo='hk'" map.r map_$1.Rout

# runs dir. is made by map.r and stores its outputs
mkdir runs/_logs
mv *.Rout runs/_logs

exit
