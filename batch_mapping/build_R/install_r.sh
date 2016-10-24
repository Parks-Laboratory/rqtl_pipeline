#!/bin/bash

# install R
tar -xzf R-3.2.5.tar.gz
cd R-3.2.5
./configure --prefix=$(pwd)
make
make install
cd ..

# install packages in R?
R-3.2.5/lib64/R/bin/Rscript install_packages.R

# edit for export
sed -i 's/R_HOME_DIR=.*/R_HOME_DIR=$(pwd)\/R/' R-3.2.5/lib64/R/bin/R

# package files for export
mv R-3.2.5/lib64/R ./
tar -czvf R.tar.gz R/

# exit
exit
