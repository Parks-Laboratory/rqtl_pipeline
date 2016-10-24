################################################################################
################################################################################
## Usage: 
##    R CMD BATCH --slave '--args rdata_file="<preprocessed inputs>.rdata" chtc_process_number="$1"' map.r
## Inputs:
## -rdata_file (see make_rdata.r for details):
##  -Fields:
##    traits: List of traits. trait_index argument specifies which trait to map with
##    mapping_jobs: List of objects containing specifics of mapping to be done
##      -Fields (per mapping_job object):
##        cross: R/QTL cross object containing genotype and phenotype information
##        sex: 'female', 'male', or 'hetero'
##        log_status: "logged" or "not-logged" specifies if log or raw trait 
##						values should be used
##        covariate_type: 'additive', or 'interactive' (see below for difference)
##        covariate_trait: name of the trait to use in covariate mapping
## Outputs:
## -The filenames indicate if males, females, or both males and females ('hetero') were used in the mapping.
## -The filenames also indicate if the log or raw values were used ('logged' vs 'not_logged')
## -When both males and females were mapped together, the filename indicates 
##  if sex was used as an additive covariate ('the average phenotype is allowed 
##  to be different in the two sexes, but the effect of the putative QTL is assumed 
##  to be the same in the two sexes.'-Karl Broman) or as both an additive covariate and 
##  an interactive covariate (allows QTL to be different in each sex)
## -Finally, there are 4 types of files generated by each mapping: 
## 		.log file has marker with highest LOD score for each chromosome
## 		.txt file has LOD scores for all markers
## 		.pdf file has the LOD plots with all markers and all chromosomes
##			(.pdf used instead of .png b/c chtc nodes can't make .pngs out of the box)
##		.rdata file has the R/QTL scanone object, which can be loaded back
##				into R to make additional plots
################################################################################
################################################################################


################################################################################
## 	Parameters for user to set
################################################################################
max_markers_to_plot = 10000   # don't plot any more than this many markers,
                              # used to determine how much of y-axis to plot


################################################################################
##	Functions and setup:	
################################################################################
if( !require(qtl) ){
  install.packages('qtl')
}
if( !require(R6) ){
  install.packages('R6')
}


#	QTL mapping	
map = function( trait, cross, sex, log_status, covariate_type, covariate_trait ){
  if( !is.na(covariate_type) ){
    output_file_naming_template = paste(c( sex, trait, covariate_type, covariate_trait, log_status), collapse = '_')
    covariate = cross$pheno[[covariate_trait]]  # e.g., sex column
    # For additive covariate the average phenotype is allowed to be different 
    # in the two sexes, but the effect of the putative QTL is assumed to
    # be the same in the two sexes. For interactive covariate, the effect of the 
	# putative QTL is also allowed to be different for each sex
    if( covariate_type == 'additive' ){
      if( log_status == 'logged' ){
        scan=scanone(cross, pheno.col = log2(cross$pheno[[trait]]), addcovar = covariate )  # calculate log of phenos  
      }else{
        scan=scanone(cross, pheno.col = trait, addcovar = covariate)
      }
    }else if( covariate_type == 'interactive' ){
      if( log_status == 'logged' ){
        scan=scanone(cross, pheno.col = log2(cross$pheno[[trait]]), addcovar = covariate, intcovar = covariate )  # calculate log of phenos  
      }else{
        scan=scanone(cross, pheno.col = trait, addcovar = covariate, intcovar = covariate)
      }
    }else{
      stop('Error: "', covariate_type, '" is not recognized. Must be either "additive" or "interactive"' )
    }
  }else{
    output_file_naming_template = paste(c( sex, trait, log_status), collapse = '_')
    if( log_status == 'logged' ){
      scan=scanone(cross, pheno.col = log2(cross$pheno[[trait]]) )  # calculate log of phenos  
    }else{
      scan=scanone(cross, pheno.col = trait )
    }
  }
  
  warnings_off()
  write_results( scan, cross, output_file_naming_template )
  warnings_on()
}

# Make files for raw lod scores, a summary of highest scores per chromosome, and lod plot
write_results = function( scan, cross, naming_template ){
  lod_file = file( normalizePath( paste(c( output_path, '/', naming_template, '_lods', '.txt' ), collapse='') ), open='wt')
  log_file = file( normalizePath( paste(c( output_path, '/', naming_template, '.log' ), collapse='') ), open='wt')
  plot_filename = normalizePath( paste( c(output_path, '/',naming_template, '_lod-plot', '.pdf'), collapse='') )
  
  write.table(summary(scan), log_file, append=TRUE, quote=FALSE, sep = ',')
  write.table(scan, lod_file, append=FALSE, quote=FALSE, sep = ',')
  
  close(lod_file)
  close(log_file)
  
  lod_column = scan$lod
  plot_title = toupper( gsub('_', ' ', naming_template) )
  pdf( file = plot_filename )	# use pdf for CHTC cluster
  # png( file = plot_filename, width=1024, height=1024, units='px')		# use png for MS Windows
  # Plot all lod-scores with values greater than those at 95th percentile
  num_markers = sum(nmar(cross))
  minimum_percentile = 1 - (max_markers_to_plot / num_markers)
  if( minimum_percentile >= 1 ){
    minimum_percentile = 0
  }
  plot(scan, main=plot_title, ylim=c(quantile(lod_column, probs = minimum_percentile)[[1]],max(lod_column)), bandcol='gray90')
  dev.off()
  
  save( list=c('scan'), file=normalizePath( paste(c( output_path, '/', naming_template, '_scan.rdata' ), collapse='')) )
}

warnings_off = function(){
  saved_warning_level <<- getOption('warn')
  options(warn = -1)
}

warnings_on = function(){
  options(warn = saved_warning_level)
}

################################################################################
##	Main program:		
################################################################################

args = commandArgs(TRUE)
for(i in 1:length(args)){
	eval(parse(text=args[[i]]))
}

load(rdata_file)  # pass rdata_file as argument to map.r

#load('rqtl_inputs.rdata')   # TODO REMOVE
number_jobs = length(mapping_jobs)
chtc_process_number = as.numeric(chtc_process_number)

# Global variables:
#chtc_process_number = 5   # TODO REMOVE

trait = traits[floor( chtc_process_number / number_jobs ) + 1]
mapping_job = mapping_jobs[[floor( chtc_process_number %% number_jobs ) + 1]]
cross = mapping_job$get_cross()
sex = mapping_job$sex
log_status = mapping_job$log_status
covariate_type = mapping_job$covariate_type
covariate_trait = mapping_job$covariate_trait

# Create output directories
dir_transfered_by_condor = 'runs'	# Must match directory name in .sub file 
dir.create(dir_transfered_by_condor)
output_path = paste(c(dir_transfered_by_condor,'/',trait), collapse='')
if( !dir.exists(output_path) ){
	if( !dir.create(output_path, recursive=TRUE) ){
	  stop( 'output dir. "', output_path, '" could not be created'  )
	}
}

# Display information in .Rout file:
sprintf('chtc_process_number: %s', chtc_process_number)
sprintf('trait: %s', trait)
sprintf('sex: %s', sex)
sprintf('log_status: %s', log_status)
sprintf('covariate_type: %s', covariate_type)
sprintf('covariate_trait: %s', covariate_trait)
sprintf('Number of markers: %s', sum(nmar(cross)))


map( trait, cross, sex, log_status, covariate_type, covariate_trait )

warnings()

closeAllConnections()
