######################################################################################################
##  Read in data
######################################################################################################
# setwd('E:/cgottsacker/rqtl/mapping_inputs')
library(qtl)

# Option 1:
cross = read.cross(
  format='csvsr'
  , crosstype="risib"
  , genfile='main_csvsr_geno.csv'
  , phefile='male_csvsr_pheno.csv'
  , na.strings=c('-')
  , genotypes=c('A','H','B')
  , alleles=c('A','B')
)

# Option 2: Alternative to read.cross(), load cross objects from .rdata file
load('rqtl_inputs.rdata')

######################################################################################################
##  Mapping using batch job's rdata file (useful for making new plots after mapping on CHTC)
######################################################################################################
mapping_job = mapping_jobs[[4]]
cross = mapping_job$get_cross()
sex = mapping_job$sex
log_status = mapping_job$log_status
covariate_trait = 'sex'
trait = 'Insulin_pg_ml'

pheno_col = cross$pheno[[trait]]
covariate = cross$pheno[[covariate_trait]]

# Optional
pheno_col = log2(pheno_col)
# covariate = log2(covariate)

# do QTL scan (pick one based on covariate_type)
scan=scanone(cross, pheno.col = pheno_col)
scan=scanone(cross, pheno.col = pheno_col, addcovar = covariate)
scan=scanone(cross, pheno.col = pheno_col, addcovar = covariate, intcovar = covariate)

# used to crop plot
num_markers = sum(nmar(cross))
minimum_percentile = 1 - (max_markers_to_plot / num_markers)
if( minimum_percentile >= 1 ){
  minimum_percentile = 0
}

# plot
lod_column = scan$lod
plot(scan, main='plot_title', ylim=c(quantile(lod_column, probs = minimum_percentile)[[1]],max(lod_column)), bandcol='gray90')
plot(scan)


######################################################################################################
##  Remove markers that are adjacent and duplicates
######################################################################################################
duplicate_markers = unlist(findDupMarkers(cross, exact.only=TRUE, adjacent.only = TRUE))
cross = drop.markers(cross, duplicate_markers)


######################################################################################################
##  General mapping
######################################################################################################
cross = calc.genoprob(cross,step=0.01, error.prob = 0.01)
cross = calc.genoprob(cross, step=0, error.prob=0.002, map.function="c-f")
trait = 'Insulin_pg_ml'
trait = 'Weight_0_wks_diet'
covariate_trait = 'sex'

perm_default = scanone(cross_default, pheno.col = log2(cross_default$pheno[[trait]]), n.perm=2000, method="hk")
perm_cf = scanone(cross_cf, pheno.col = log2(cross_cf$pheno[[trait]]), n.perm=2000, method="hk")

pheno_col = cross$pheno[[trait]]
covariate = cross$pheno[[covariate_trait]]

# Optional
pheno_col = log2(pheno_col)
# covariate = log2(covariate)

# do QTL scan (pick one based on covariate_type)
scan=scanone(cross, pheno.col = pheno_col)
scan=scanone(cross, pheno.col = pheno_col, addcovar = covariate)
scan=scanone(cross, pheno.col = pheno_col, addcovar = covariate, intcovar = covariate)


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
trait = 'Insulin_pg_ml'
cross = calc.genoprob(cross,step=0.01, error.prob = 0.01, stepwidth = "fixed")
cross = reduce2grid(cross)

# HK (30 minutes per trait, for 50k markers)
t = proc.time()
perm_hk = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), n.perm=2000, method="hk")
proc.time() - t

scan_hk = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), method = "hk" )
summary(perm_hk)
summary(scan_hk, perms=perm_hk, alpha=0.2, pvalues=TRUE)

# EM (12 hours per trait, for 50k markers)
t = proc.time()
perm_em = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), n.perm=1000, method="em")
proc.time() - t

scan_em = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), method = "em" )
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
