from src.get_rqtl import *
import unittest

class test__init__(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male']

	def test_minimal(self):
		self.individual_averaged = Individual_averaged(self.line, 'female')
		self.assertTrue(self.individual_averaged.is_female())
		self.individual_averaged = Individual_averaged(self.line, 'male')
		self.assertTrue(self.individual_averaged.is_male())

		self.assertNotIn('not_a_sex', sex_label_as_numeric)


class test_add(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male', '-']
		self.missing_value = Individual_averaged.missing_value
		self.individual_averaged = Individual_averaged(self.line, 'female')
		self.assertEqual(self.missing_value, '-')

	def test_minimal(self):
		self.individual_averaged.add(self.line)


class test_round_sigfigs(unittest.TestCase):
	def setUp(self):
		self.integer_values = [3434, 343, 34, -34,  39723324]
		self.decimal_values = [343.3, .34, -.34, .32437932478327,]

	def assertRoundEqual(self, value, target_num_sigfigs, correct_rounding):
		self.assertEqual( str(round_sigfigs(value, target_num_sigfigs)), str(correct_rounding))

	def test_integer_values(self):
		# normal cases
		self.assertRoundEqual(343, 3, '343' )
		self.assertRoundEqual(343, 2, '340' )
		self.assertRoundEqual(343, 1, '300' )
		self.assertRoundEqual(343, 0, '0' )

		# special cases
		self.assertRoundEqual(343, 4, '343' )
		self.assertRoundEqual(397, 2, '400' )

	def test_decimal_values(self):
		'''
		Stuck getting 1 decimal place of precision, but given that R/QTL
		coerces all values for a given trait to have same decimal precision,
		nit-picking over this is waste of effort.
		'''
		self.assertRoundEqual(34.3, 2, '34.0' )
		self.assertRoundEqual(347.3, 2, '350.0' )
		self.assertRoundEqual(347345.3, 2, '350000.0' )
		self.assertRoundEqual(3.473453, 3, '3.47' )
		self.assertRoundEqual(3.473453, 4, '3.473' )
		self.assertRoundEqual(3.473453, 5, '3.4735' )
		self.assertRoundEqual(3.473553, 5, '3.4734' )

	def demonstrate_unavoidable_behavior(self):
		self.assertRoundEqual(0.000, 3, '0.0' )
		self.assertRoundEqual(0, 1, '0' )


class test_average(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male']
		self.individual_averaged = Individual_averaged(self.line, 'female')

	def test(self):
		# average = 24.3
		self.assertEqual('2E+1' , self.individual_averaged.average(['23.3','3','46.6']))
		values = ['-']




if __name__ == '__main__':
	suite_names = [test__init__, test_add, test_average]
	all_suites = []
	for suite_name in suite_names:
		suites.add(unittest.TestLoader().loadTestsFromTestCase(suite_name))
	all_tests = unittest.TestSuite(all_suites)
	unittest.TextTestRunner(verbosity=2).run(all_tests)
