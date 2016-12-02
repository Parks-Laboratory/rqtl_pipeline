# Usage: R CMD BATCH --slave '--args rdata_file="<preprocessed inputs>.rdata" chtc_process_number="$1"' map.r
# See README.md for more details


################################################################################
## 	Parameters for user to set
################################################################################
max_markers_to_plot = 10000	 # don't plot any more than this many markers,
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

# Returns true if a column only contains 0 or 1 (binary values to indicate discrete value)
is_binary_indicator = function(col){
	unique_values = unique(col)
	has_0 = (0 %in% unique_values)
	has_1 = (1 %in% unique_values)
	return( (length(unique_values) == 2 && has_0 && has_1) ||
		((length(unique_values) == 1) && (has_0 || has_1) ) )
}

#	QTL mapping
map = function( trait, cross, sex, log_status, covariate_type, covariate_trait, scan_algo, plot, summary, rdata ){
	pheno_col = cross$pheno[[trait]]

	# log2(0) == -Inf, which would not be good
	if( log_status == 'logged'){
		if(!(0 %in% pheno_col) ){
			pheno_col = log2(pheno_col)
		}else if( is_binary_indicator(pheno_col) ){
			sprintf('Trait "%s" is a binary indicator containing the value "0". Values not logged.', pheno_col)
		}
		else{
			stop('Error: "', pheno_col, '" contains the value "0" and cannot be logged' )
		}
	}

	if( !is.na(covariate_type) ){
		output_file_naming_template = paste(c( sex, trait, covariate_type, covariate_trait, log_status), collapse = '_')

		covariate = cross$pheno[[covariate_trait]]	# e.g., sex column
		# log2(0) == -Inf, which would not be good
		if( log_status == 'logged'){
			if(!(0 %in% covariate) ){
				covariate = log2(covariate)
			}else if( is_binary_indicator(covariate) ){
				sprintf('Trait "%s" is a binary indicator containing the value "0". Values not logged.', covariate_trait)
			}
			else{
				stop('Error: "', covariate_trait, '" contains the value "0" and cannot be logged' )
			}
		}

		if( covariate_type == 'additive' ){
			scan=scanone(cross, method=scan_algo, pheno.col = pheno_col, addcovar = covariate)
		}else if( covariate_type == 'interactive' ){
			scan=scanone(cross, method=scan_algo, pheno.col = pheno_col, addcovar = covariate, intcovar = covariate)
		}else{
			stop('Error: "', covariate_type, '" is not recognized. Must be either "additive" or "interactive"' )
		}
	}else{
		output_file_naming_template = paste(c( sex, trait, log_status), collapse = '_')
		scan=scanone(cross, method=scan_algo, pheno.col = pheno_col )
	}

	warnings_off()
	write_mapping_results( scan, cross, output_file_naming_template, plot, summary, rdata )
	warnings_on()
}

# Make files for raw lod scores, a summary of highest scores per chromosome, and lod plot
write_mapping_results = function( scan, cross, naming_template, plot, summary, rdata ){
	# print column 1 (chromosome #), and column 3 (lod value),
	# but don't print column 2 (estimated centiMorgans) which is made-up
	lod_file = file( normalizePath( paste(c( output_path, '/', naming_template, '_lods', '.txt' ), collapse='') ), open='wt')
	write.table(scan[,c(1,3)], lod_file, append=FALSE, quote=FALSE, sep = ',')
	close(lod_file)
	if(summary){
		log_file = file( normalizePath( paste(c( output_path, '/', naming_template, '.log' ), collapse='') ), open='wt', append = TRUE)
		write.table(summary(scan)[,c(1,3)], log_file, append=TRUE, quote=FALSE, sep = ',')
		close(log_file)
	}

	if(plot){
		plot_filename = normalizePath( paste( c(output_path, '/',naming_template, '_lod-plot', '.pdf'), collapse='') )
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
	}

	if(rdata){
		save( list=c('scan'), file=normalizePath( paste(c( output_path, '/', naming_template, '_scan.rdata' ), collapse='')) )
	}

}

calculate_thresholds = function(cross, trait, scan_algo) {
	perm = scanone(cross, pheno.col = log2(cross$pheno[[trait]]), n.perm=2000, method=scan_algo)
	write_threshold_results(summary(perm))
}

write_threshold_results = function(summary) {
	threshold_file = file( normalizePath( paste(c( output_path, '/threshold.log' ), collapse='') ), open='wt')
	write.table(summary, threshold_file, append=TRUE, quote=FALSE)
	close(threshold_file)
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

load(rdata_file)	# pass rdata_file as argument to map.r

#load('rqtl_inputs.rdata')	 # TODO REMOVE
number_jobs = length(mapping_jobs)
chtc_process_number = as.numeric(chtc_process_number)

# Global variables:
#chtc_process_number = 5	 # TODO REMOVE

trait = traits[floor( chtc_process_number / number_jobs ) + 1]
mapping_job = mapping_jobs[[floor( chtc_process_number %% number_jobs ) + 1]]
cross = mapping_job$get_cross()
sex = mapping_job$sex
log_status = mapping_job$log_status
covariate_type = mapping_job$covariate_type
covariate_trait = mapping_job$covariate_trait

# Create output directories
dir_transfered_by_condor = 'runs'	# Must match directory name in .sub file
dir.create(dir_transfered_by_condor)	# Condor will transfer this file back to submit server
output_path = paste(c(dir_transfered_by_condor,'/',trait), collapse='')
if( !dir.exists(output_path) ){
	if( !dir.create(output_path, recursive=TRUE) ){
		stop( 'output dir. "', output_path, '" could not be created'	)
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

calculate_thresholds(cross, trait, scan_algo)

map( trait, cross, sex, log_status, covariate_type, covariate_trait, scan_algo, plot, summary, rdata )

warnings()

closeAllConnections()
