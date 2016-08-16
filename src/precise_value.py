class precise_value(object):
    def num_decimal_digits(value):
    	'''Counts number of significant digits to right of decimal point'''
    	parsed_value = remove_non_digits(value)
    	parsed_value = remove_non_significant_zeroes(parsed_value)
    	parsed_value = parsed_value.split('.')[1]
    	return( len(parsed_value) )

    def num_sigfigs(value):
    	'''
    	Counts number of significant figures in a numeric string.
    	TODO: replace regex w/ conditional logic (regex decreased efficiency by 10%)
    	'''
    	parsed_value = remove_non_digits(value)
    	parsed_value = remove_non_significant_zeroes(parsed_value)
    	# remove decimal point
    	parsed_value = re.sub(r'\.', r'', parsed_value)
    	return( len(parsed_value) )

    def remove_non_digits(value):
    	'''Remove scientific notation characters and negation sign
    		-03.05E+4 -> 03.05'''
    	return( re.sub(r'^-*((\d+\.?\d*)|(\d*\.\d+)).*$', r'\1', value) )

    def remove_non_significant_zeroes(value):
    	# remove leading zeroes to left of decimal point, keeping at most 1 zero
    	# e.g. -03.05E+4 -> 305E+4    or    05 -> 5    or   0.4 -> .4    or   00 -> 0
    	parsed_value = re.sub(r'^0*(\d.*)$', r'\1', value)
    	# remove leading zeroes to right of decimal point, plus any immediately to
    	# the left of decimal point, if value < 1
    	# e.g. .05E+4 -> 5E+4    or   0.01 -> .1
    	parsed_value = re.sub(r'^0*(\.)0*(\d+)$', r'\1\2', parsed_value)
    	# remove trailing zeroes to right of integer w/ no decimal point
    	# e.g. 100 -> 1   but   100. -> 100.
    	parsed_value = re.sub(r'^([1-9]+)0*$', r'\1', parsed_value)
    	return( parsed_value )
