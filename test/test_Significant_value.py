from src.get_rqtl import *
import unittest

class test_Significant_value_max(unittest.TestCase):
	'''Test implementation of Significant_value class

	In particular tests implementation where rounding_method == Rounding_method.max'''

	def assertRoundingEqual(self, sum, average, correctly_rounded_value):
		'''Wrapper function to test Significant_value.round()

		Compare string value of rounded value with correctly_rounded_value
		Accesses rounding_method from user-set global variable in get_rqtl.py'''
		rounding_method = Rounding_method.max
		self.assertEqual(
			str(Significant_value.round(Decimal(sum), Decimal(average), rounding_method))
			,correctly_rounded_value )

	def assertSumEqual(self, values, correct_sum):
		self.assertEqual(str(Significant_value.sum(values)), correct_sum)

	def test_round_fixed_point(self):
		# no rounding required, sigfigs of sum >= sigfigs of average
		self.assertRoundingEqual('10.10','5.050','5.050')
		self.assertRoundingEqual('10.10','5.05','5.05')
		self.assertRoundingEqual('-10.10','-5.05','-5.05')
		self.assertRoundingEqual('1','1','1')
		self.assertRoundingEqual('5.555E+5','9.999E+3','9999')
		self.assertRoundingEqual('5E+5','1E+4','1E+4')
		self.assertRoundingEqual('0','0','0')

		# round up
		self.assertRoundingEqual('12571','345.637','345.64')
		self.assertRoundingEqual('-1.25E-3','-.0063716515','-0.00637')

		# round down
		self.assertRoundingEqual('1257','3456.37','3456')
		self.assertRoundingEqual('1257','34.5637','34.56')
		self.assertRoundingEqual('1257','34.560','34.56')

	def test_sum(self):
		self.assertSumEqual(['1','2','3'], '6')
		self.assertSumEqual(['3.55', '6.55'], '10.10')

	def test_num_significant_digits(self):
		'''Count integral placeholding zeroes as significant'''
		nsd = Significant_value.num_significant_digits

		self.assertEqual(nsd('0'), 1)
		self.assertEqual(nsd('1'), 1)
		self.assertEqual(nsd('10'), 2)
		self.assertEqual(nsd('11'), 2)
		self.assertEqual(nsd('00'), 1)
		self.assertEqual(nsd('01'), 1)
		self.assertEqual(nsd('010'), 2)
		self.assertEqual(nsd('011'), 2)
		self.assertEqual(nsd('-0.1'), 1)
		self.assertEqual(nsd('-1.1'), 2)
		self.assertEqual(nsd('-1'), 1)
		self.assertEqual(nsd('-10'), 2)
		self.assertEqual(nsd('-001'), 1)
		self.assertEqual(nsd('-010'), 2)
		self.assertEqual(nsd('10.'), 2)
		self.assertEqual(nsd('10E4'), 2)
		self.assertEqual(nsd('10.E4'), 2)
		self.assertEqual(nsd('.02E4'), 1)
		self.assertEqual(nsd('-1.2E3'), 2)
		self.assertEqual(nsd('1.2E3'), 2)
		self.assertEqual(nsd('1.1'), 2)
		self.assertEqual(nsd('0.0'), 1)
		self.assertEqual(nsd('-0.1'), 1)
		self.assertEqual(nsd('-01.1'), 2)
		self.assertEqual(nsd('-01.2E3'), 2)
		self.assertEqual(nsd('0.1'), 1)
		self.assertEqual(nsd('01.1'), 2)
		self.assertEqual(nsd('01.2E3'), 2)

		self.assertEqual(nsd('123456789'), 9)
		self.assertEqual(nsd('12345.6789'), 9)
		self.assertEqual(nsd('.123456789'), 9)
		self.assertEqual(nsd('1.5'), 2)
		self.assertEqual(nsd('2'), 1)
		self.assertEqual(nsd('-3'), 1)
		self.assertEqual(nsd('05'), 1)
		self.assertEqual(nsd('1.001'), 4)
		self.assertEqual(nsd('1.00'), 3)
		self.assertEqual(nsd('100'), 3)
		self.assertEqual(nsd('100.'), 3)
		self.assertEqual(nsd('0'), 1)
		self.assertEqual(nsd('0.0'), 1)
		self.assertEqual(nsd('.5'), 1)
		self.assertEqual(nsd('0.5'), 1)
		self.assertEqual(nsd('0.000243'), 3)
		self.assertEqual(nsd('.00003'), 1)
		self.assertEqual(nsd('05.5E+1'), 2)
		self.assertEqual(nsd('3E+5'), 1)
		self.assertEqual(nsd('5E-7'), 1)
		self.assertEqual(nsd('5.34E-7'), 3)
		self.assertEqual(nsd('05.34E-7'), 3)
		self.assertEqual(nsd('-05.34E-7'), 3)


class test_Significant_value(unittest.TestCase):
	def test_remove_decimal_point(self):
		rdp = Significant_value.remove_decimal_point

		# test if decimal point removed if string contains one
		self.assertEqual(rdp('.'), '')
		self.assertEqual(rdp('1.'), '1')
		self.assertEqual(rdp('.1'), '1')
		self.assertEqual(rdp('-.1'), '-1')
		self.assertEqual(rdp('-1.2E3'), '-12E3')

		# test if string unchanged if string doesn't contain a decimal point
		self.assertEqual(rdp('1248'), '1248')
		self.assertEqual(rdp('1200'), '1200')
		self.assertEqual(rdp('1'), '1')
		self.assertEqual(rdp('01'), '01')
		self.assertEqual(rdp('1E3'), '1E3')

	def test_remove_non_digits(self):
		rnd = Significant_value.remove_non_digits

		# test if negation sign and scientific notation are removed
		self.assertEqual(rnd('-.1'), '.1')
		self.assertEqual(rnd('-1.1'), '1.1')
		self.assertEqual(rnd('-1'), '1')
		self.assertEqual(rnd('-10'), '10')
		self.assertEqual(rnd('-1.2E3'), '1.2')
		self.assertEqual(rnd('1.2E3'), '1.2')

		# test if anything is removed which shouldn't be
		self.assertEqual(rnd('1'), '1')
		self.assertEqual(rnd('11'), '11')
		self.assertEqual(rnd('1.1'), '1.1')
		self.assertEqual(rnd('.1'), '.1')
		self.assertEqual(rnd('10'), '10')
		self.assertEqual(rnd('1.0'), '1.0')
		self.assertEqual(rnd('0.1'), '0.1')

	def test_remove_leading_zeroes(self):
		rlz = Significant_value.remove_leading_zeroes

		# test if leading integral zeros are removed
		self.assertEqual(rlz('0.0'), '.0')
		self.assertEqual(rlz('00'), '0')
		self.assertEqual(rlz('01'), '1')
		self.assertEqual(rlz('010'), '10')
		self.assertEqual(rlz('011'), '11')
		self.assertEqual(rlz('-0.1'), '-.1')
		self.assertEqual(rlz('-01.1'), '-1.1')
		self.assertEqual(rlz('-001'), '-1')
		self.assertEqual(rlz('-010'), '-10')
		self.assertEqual(rlz('-01.2E3'), '-1.2E3')
		self.assertEqual(rlz('0.1'), '.1')
		self.assertEqual(rlz('01.1'), '1.1')
		self.assertEqual(rlz('01.2E3'), '1.2E3')

		# test if anything removed that shouldn't be
		self.assertEqual(rlz('0.'), '0.')
		self.assertEqual(rlz('0'), '0')
		self.assertEqual(rlz('-0.1'), '-.1')
		self.assertEqual(rlz('-1.1'), '-1.1')
		self.assertEqual(rlz('-1'), '-1')
		self.assertEqual(rlz('-10'), '-10')
		self.assertEqual(rlz('-1.2E3'), '-1.2E3')
		self.assertEqual(rlz('0.1'), '.1')
		self.assertEqual(rlz('1.1'), '1.1')
		self.assertEqual(rlz('1'), '1')
		self.assertEqual(rlz('10'), '10')
		self.assertEqual(rlz('11'), '11')
		self.assertEqual(rlz('1.2E3'), '1.2E3')

	def test_remove_decimal_placeholding_zeroes(self):
		rdpz= Significant_value.remove_decimal_placeholding_zeroes

		# test if zeroes removed
		self.assertEqual(rdpz('0.0'), '.0')
		self.assertEqual(rdpz('0.00'), '.0')
		self.assertEqual(rdpz('.00'), '.0')
		self.assertEqual(rdpz('.03'), '.3')
		self.assertEqual(rdpz('0.03'), '.3')
		self.assertEqual(rdpz('-0.0'), '-.0')
		self.assertEqual(rdpz('-0.00'), '-.0')
		self.assertEqual(rdpz('-.00'), '-.0')
		self.assertEqual(rdpz('-.03'), '-.3')
		self.assertEqual(rdpz('-0.03'), '-.3')

		# test if anything removed that shouldn't be
		self.assertEqual(rdpz('0'), '0')
		self.assertEqual(rdpz('-0.1'), '-.1')
		self.assertEqual(rdpz('-1.1'), '-1.1')
		self.assertEqual(rdpz('-1'), '-1')
		self.assertEqual(rdpz('-10'), '-10')
		self.assertEqual(rdpz('-1.2E3'), '-1.2E3')
		self.assertEqual(rdpz('0.1'), '.1')
		self.assertEqual(rdpz('1.1'), '1.1')
		self.assertEqual(rdpz('1'), '1')
		self.assertEqual(rdpz('10'), '10')
		self.assertEqual(rdpz('11'), '11')
		self.assertEqual(rdpz('1.2E3'), '1.2E3')

	def test_remove_integral_placeholding_zeroes(self):
		 ripz = Significant_value.remove_integral_placeholding_zeroes

		 # test if zeroes removed
		 self.assertEqual(ripz('-10'), '-1')
		 self.assertEqual(ripz('10'), '1')

		 # test if anything removed that shouldn't be
		 self.assertEqual(ripz('0'), '0')
		 self.assertEqual(ripz('0.1'), '0.1')
		 self.assertEqual(ripz('1.1'), '1.1')
		 self.assertEqual(ripz('1'), '1')
		 self.assertEqual(ripz('11'), '11')
		 self.assertEqual(ripz('10.'), '10.')
		 self.assertEqual(ripz('10E4'), '10E4')
		 self.assertEqual(ripz('10.E4'), '10.E4')
		 self.assertEqual(ripz('-0.1'), '-0.1')
		 self.assertEqual(ripz('-1.1'), '-1.1')
		 self.assertEqual(ripz('-1'), '-1')
		 self.assertEqual(ripz('-1.2E3'), '-1.2E3')
		 self.assertEqual(ripz('1.2E3'), '1.2E3')
