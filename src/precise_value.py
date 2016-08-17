from enum import Enum
from decimal import Decimal
import sys

class Precise_value(object):

    def __init__(self, rounding_method, value):
        self.rounding_handler = set_rounding_handler(rounding_method, value)
        self.string_value = value
        self.decimal_value = Decimal(value)

    def set_rounding_handler(self, rounding_method, value):
        if rounding_method == 'no_rounding':
            self.rounding_handler = Rounding_handler(value)
        elif rounding_method == 'keep_integral_zeroes':
            self.rounding_handler = Rounding_handler_keep_integral_zeroes(value)
        elif rounding_method == 'proper':
            self.rounding_handler = Rounding_handler_proper(value)
        else:
            sys.exit('Error: rounding_method "' + rounding_method + '" does not exist.')

    def __add__(self, other):
        if self.can_do_arithmetic(other):
            return( self.rounding_handler.add(self, other) )

    def __sub__(self, other):
        if self.can_do_arithmetic(other):
            return( self.rounding_handler.sub(self, other) )
            # TODO impelemnt

    def __mul__(self, other):
        if self.can_do_arithmetic(other):
            return( self.rounding_handler.mul(self, other) )
            # TODO impelemnt

    def __div__(self, other):
        if self.can_do_arithmetic(other):
            return( self.rounding_handler.div(self, other) )
            # TODO impelemnt

    def can_do_arithmetic(self, other):
        return( is_precise_value_object(other) and self.are_rounding_handlers_same(other) )

    def is_precise_value_object(value):
        return(isinstance(value, Precise_value))

    def are_rounding_handlers_same(self, other):
        return(self.rounding_handler.__class__ is other.rounding_handler.__class__)

class Rounding_handler(object):
    self.num_significant_digits = num_significant_digits(string_value)
    self.num_significant_decimal_digits = num_significant_decimal_digits(string_value)

    def __init__(self, value):
        if method in rounding_handlers.__members__.keys():
            self.method = method
            # TODO reset num_significant_digits & num_significant_decimal_digits
        else: sys.exit('Error: unsupported rounding method specified')

    def round_decimal_digits(self, value, num_digits_to_keep):
         return( value.quantize(Decimal(str(pow(10,-num_digits_to_keep))),
                     rounding=ROUND_HALF_EVEN) )

    def num_significant_decimal_digits(value):
        '''Counts number of significant digits to right of decimal point'''
        parsed_value = remove_non_digits(value)
        parsed_value = remove_non_significant_decimal_placeholding_zeroes(parsed_value)
        parsed_value = parsed_value.split('.')[1]
        return( len(parsed_value) )

    def num_significant_digits(value):
        '''
        Counts number of significant figures in a numeric string.
        TODO: replace regex w/ conditional logic (regex decreased efficiency by 10%)
        '''
        # TODO conditional logic based on method
        parsed_value = remove_non_digits(value)
        parsed_value = remove_non_significant_leading_zeroes(parsed_value)
        parsed_value = remove_non_significant_decimal_placeholding_zeroes(parsed_value)
        num_significant_digits = len(parsed_value)
        if round.proper is method:
        # remove decimal point
        parsed_value = re.sub(r'\.', r'', parsed_value)
        return( len(parsed_value) )

    def remove_non_digits(value):
        '''Remove scientific notation characters and negation sign
        	-03.05E+4 -> 03.05'''
        return( re.sub(r'^-*((\d+\.?\d*)|(\d*\.\d+)).*$', r'\1', value) )

    def remove_non_significant_zeroes(value):
        '''Abstract method, inherit this class, and implement it'''
        sys.exit('Error: Abstract method must be implemented in subclass')

    def remove_non_significant_leading_zeroes(value):
        '''remove leading zeroes to left of decimal point, keeping at most 1 zero
        e.g. -03.05E+4 -> 305E+4    or    05 -> 5    or   0.4 -> .4    or   00 -> 0'''
        return( re.sub(r'^0*(\d\.?\d*)$', r'\1', value) )

    def remove_non_significant_decimal_placeholding_zeroes(value):
        '''remove leading zeroes to right of decimal point, plus any immediately to
        the left of decimal point, if value < 1
        e.g. .05 -> 5    or   0.01 -> .1'''
        return( re.sub(r'^0*(\.)0*(\d+)$', r'\1\2', parsed_value) )

    def remove_non_significant_integral_placeholding_zeroes(value):
        '''remove trailing zeroes to right of integer w/ no decimal point
        e.g. 100 -> 1   but   100. -> 100.'''
        return( parsed_value = re.sub(r'^([1-9]+)0*$', r'\1', parsed_value) )
