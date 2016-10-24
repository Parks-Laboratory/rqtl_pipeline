################################################################################
################################################################################
## Instructions:
##		-Set parameters below, and also decide which tests to run and set
##		mapping_jobs accordingly
##			-input_path must specify the directory containing the genotype
##			and phenotype files. Use setwd() in interactive session
##		-Run script in an interactive R session after setting setwd()
##		OR Run script from command line after editing fields in this script
##
################################################################################
################################################################################


################################################################################
## 	Parameters for user to set
################################################################################
# setwd('E:/cgottsacker/chtc/mapping_files')
input_path = '.'
geno_filename = 'main_csvsr_geno.csv'
female_filename = 'female_csvsr_pheno.csv'
male_filename = 'male_csvsr_pheno.csv'
hetero_filename = 'hetero_csvsr_pheno.csv'
traits_filename = 'phenotypes_list.txt'
covariate_trait = 'sex'

# ALSO: set mapping_jobs below (under "Main script")

################################################################################
##	Functions and setup
################################################################################
if( !require(qtl) ){
  install.packages('qtl')
}
if( !require(R6) ){
  install.packages('R6')
}

# Object containing specifics of mapping to be done
mapping_job = R6Class("mapping_job",
                      public = list(
                        cross = NA,
                        sex = NA,
                        log_status = NA,
                        covariate_type = NA,
                        covariate_trait = NA,
                        initialize = function(sex, log_status, covariate_type, covariate_trait){
                          self$sex = sex
                          self$log_status = log_status
                          self$covariate_type = covariate_type
                          self$covariate_trait = covariate_trait
                        },
                        get_cross = function(){
                          if( self$sex == 'female' ){
                            self$cross = female_cross
                          }else if( self$sex == 'male' ){
                            self$cross = male_cross
                          }else if( self$sex == 'hetero'){
                            self$cross = hetero_cross
                          }
                          return(self$cross)
                        }
                      )
)

read_data = function(input_path, geno_filename, pheno_filename){
  return( read.cross(
    format='csvsr'
    , dir=input_path
    , genfile=geno_filename
    , phefile=pheno_filename
    , na.strings=c('-')
    , genotypes=c('A','H','B')
    , alleles=c('A','B') )
  )
}

################################################################################
## Main script
################################################################################
female_cross = read_data(input_path, geno_filename, female_filename)
male_cross = read_data(input_path, geno_filename, male_filename)
hetero_cross = read_data(input_path, geno_filename, hetero_filename)

traits = scan(traits_filename, what='', sep='\n')

# just looks at genetics, so any cross will return same results
duplicate_markers = unlist(findDupMarkers(female_cross, exact.only=TRUE, adjacent.only = TRUE))

female_cross = drop.markers(female_cross, duplicate_markers)
male_cross = drop.markers(male_cross, duplicate_markers)
hetero_cross = drop.markers(hetero_cross, duplicate_markers)

# mapping_job$new(cross, sex, log_status, covariate_type, covariate_trait)
#		cross: R/QTL cross object containing genotype and phenotype information
#		sex: 'female', 'male', or 'hetero'
#		log_status: "logged" or "not-logged" specifies if log or raw trait
#				values should be used
#		covariate_type: 'additive', or 'interactive'
#		covariate_trait: name of the trait to use in covariate mapping
#
# For each trait, do the following tests:
mapping_jobs = c( mapping_job$new('female', 'logged', NA, NA),
                  mapping_job$new('male', 'logged', NA, NA),
                  mapping_job$new('hetero', 'logged', 'additive', covariate_trait),
                  mapping_job$new('hetero', 'logged', 'interactive', covariate_trait)
)

save(list=c('mapping_jobs','female_cross','male_cross','hetero_cross','traits'), file="rqtl_inputs.rdata", compress = TRUE )
