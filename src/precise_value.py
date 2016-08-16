from enum import Enum
import sys

class Precise_value(object):
    rounding_methods = Enum('rounding_methods',
            'proper proper_keep_integral_zeroes')

    def __init__(self, value):
        self.rounding_method = Precise_value.rounding_methods.proper_keep_integral_zeroes
        self.string_value = value
        self.decimal_value = Decimal(value)
        self.num_significant_digits = num_significant_digits(string_value)
        self.num_significant_decimal_digits = num_significant_decimal_digits(string_value)

    def __add__(self, other):
        # TODO impelemnt

    def __sub__(self, other):
        # TODO impelemnt

    def __mul__(self, other):
        # TODO impelemnt

    def __div__(self, other):
        # TODO impelemnt

    def set_rounding_method(self, rounding_method):
        if rounding_method in Precise_value.rounding_methods.__members__.keys()
            self.rounding_method = rounding_method
            # TODO reset num_significant_digits & num_significant_decimal_digits
        else: sys.exit('Error: unsupported rounding method specified')

    def num_significant_decimal_digits(value):
    	'''Counts number of significant digits to right of decimal point'''
    	parsed_value = remove_non_digits(value)
    	parsed_value = remove_non_significant_zeroes(parsed_value)
    	parsed_value = parsed_value.split('.')[1]
    	return( len(parsed_value) )

    def num_significant_digits(value):
    	'''
    	Counts number of significant figures in a numeric string.
    	TODO: replace regex w/ conditional logic (regex decreased efficiency by 10%)
    	'''
        # TODO conditional logic based on rounding_method
    	parsed_value = remove_non_digits(value)
    	parsed_value = remove_non_significant_zeroes(parsed_value)
    	# remove decimal point
    	parsed_value = re.sub(r'\.', r'', parsed_value)
    	return( len(parsed_value) )

    def remove_non_digits(value):
    	'''Remove scientific notation characters and negation sign
    		-03.05E+4 -> 03.05'''
    	return( re.sub(r'^-*((\d+\.?\d*)|(\d*\.\d+)).*$', r'\1', value) )

    def remove_non_significant_leading_zeroes(value):
    	'''remove leading zeroes to left of decimal point, keeping at most 1 zero
    	e.g. -03.05E+4 -> 305E+4    or    05 -> 5    or   0.4 -> .4    or   00 -> 0'''
    	return( re.sub(r'^0*(\d\.?\d*)$', r'\1', value) )

    def remove_non_significant_decimal_placeholding_zeroes(value):
    	'''remove leading zeroes to right of decimal point, plus any immediately to
    	the left of decimal point, if value < 1
    	e.g. .05 -> 5    or   0.01 -> .1'''
    	parsed_value = re.sub(r'^0*(\.)0*(\d+)$', r'\1\2', parsed_value)

    def remove_non_significant_integral_placeholding_zeroes(value):
    	'''remove trailing zeroes to right of integer w/ no decimal point
    	e.g. 100 -> 1   but   100. -> 100.'''
    	parsed_value = re.sub(r'^([1-9]+)0*$', r'\1', parsed_value)
    	return( parsed_value )
