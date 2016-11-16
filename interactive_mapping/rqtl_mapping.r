######################################################################################################
##  Read in data
######################################################################################################
# setwd('E:/cgottsacker/rqtl/mapping_inputs')
library(qtl)

# Option 1:
cross = read.cross(
  format='csvsr'
  , dir='directory/containing/genfile_and_phefile'
  , genfile='main_csvsr_geno.csv'
  , phefile='male_csvsr_pheno.csv'
  , na.strings=c('-')
  , genotypes=c('A','H','B')
  , alleles=c('A','B')
)

# Option 2: Alternative to read.cross(), load cross objects from .rdata file
load('rqtl_inputs.rdata')

######################################################################################################
##  Remove markers that are adjacent and duplicates
######################################################################################################
duplicate_markers = unlist(findDupMarkers(cross, exact.only=TRUE, adjacent.only = TRUE))
cross = drop.markers(cross, duplicate_markers)

######################################################################################################
##  Figure out why warnings crop up for covariate mapping
######################################################################################################
covariate = 'sex'
trait = 'Insulin_pg_ml'
cross = calc.genoprob(cross,step=0.01, error.prob = 0.01)
scan=scanone(cross, pheno.col = log2(cross$pheno[[trait]]), chr = 8 )
scan=scanone(cross, pheno.col = log2(cross$pheno[[trait]]), addcovar = covariate, chr = 8 )
scan=scanone(cross, pheno.col = log2(cross$pheno[[trait]]), addcovar = covariate, intcovar = covariate, chr = 8 )
summary(scan)
plot(scan, xlab = '(Base Pair Position)/2e6' )
plot(scan, chr = '8', xlim = c(7e6,2e7), main = 'Chromosome 8', xlab = '(Base Pair Position)/2' )

######################################################################################################
##  Examine effects of different step-sizes for male_insulin_step_0.001_error_0.01_chr_8
######################################################################################################
trait = 'Insulin_pg_ml'
cross = calc.genoprob(cross,step=0.001, error.prob = 0.01)
scan = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), chr = 8 )
plot(scan, main = "Step 0.001")
summary(scan)

######################################################################################################
##  Examine lod significance-threshold given by permutation testing
######################################################################################################
trait = 'Weight_0_wks_diet'
cross = calc.genoprob(cross,step=0.01, error.prob = 0.01, stepwidth = "fixed")
cross = reduce2grid(cross)

# HK
perm_hk = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), n.perm=1000, method="hk")
scan_hk = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), chr = 8, method = "hk" )
summary(perm_hk)
summary(scan_hk, perms=perm_hk, alpha=0.2, pvalues=TRUE)

# EM
perm_em = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), n.perm=1000, method="em")
scan_em = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), chr = 8, method = "em" )
summary(perm_em)
summary(scan_em, perms=perm_em, alpha=0.2, pvalues=TRUE)

######################################################################################################
##  Compare effects of different missing-value-guessing-algorithms
######################################################################################################
trait = 'Insulin_pg_ml'
cross_step = calc.genoprob(cross,step=0.001, error.prob = 0.01)
scan.em = scanone(cross_step, pheno.col = log2(cross_step$pheno[[trait]]), chr = 8 )
scan.hk = scanone(cross_step, pheno.col = log2(cross_step$pheno[[trait]]), chr = 8 , method = "hk")
plot(scan.em, main = "EM, Step 0.001")
plot(scan.hk, main = "HK, Step 0.001")

plot(scan.hk - scan.em, ylim=c(-0.3, 3), ylab="LOD(HK)-LOD(EM)", main=trait, chr = 8)
summary(scan.hk)

######################################################################################################
##  Examine effects of using reduce2grid() between calc.genoprob() and scanone()
######################################################################################################
# w/o using reduce2grid()
trait = 'Insulin_pg_ml'
cross = calc.genoprob(cross,step=0.001, error.prob = 0.01)
scan = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), chr = 8 )
plot(scan, chr = '8', main = 'Male, insulin, chromosome 8, all markers, step 0.001, error 0.01', xlab = '(Base Pair Position)/2e6' )
cross_all = cross
scan_all = scan

# using reduce2grid()
trait = 'Insulin_pg_ml'
cross = calc.genoprob(cross,step=0.001, error.prob = 0.01, stepwidth = "fixed")
cross = reduce2grid(cross)
scan = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), chr = 8 )
plot(scan, chr = '8', main = 'Male, insulin, chromosome 8, reduced markers, step 0.001, error 0.01', xlab = '(Base Pair Position)/2e6', incl.markers=FALSE)
cross_reduced = cross
scan_reduced = scan
