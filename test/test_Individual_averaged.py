from src.get_rqtl import *
import unittest

class test__init__(unittest.TestCase):
	def setUp(self):
		self.line=['iid','strain','male']

	def test_minimal(self):
		self.individual_averaged=Individual_averaged(self.line, 'female')
		self.assertTrue(self.individual_averaged.is_female())
		self.individual_averaged=Individual_averaged(self.line, 'male')
		self.assertTrue(self.individual_averaged.is_male())

		self.assertNotIn('not_a_sex', sex_label_as_numeric)


class test_add(unittest.TestCase):
	def setUp(self):
		self.line=['iid','strain','male', '-']
		self.missing_value=Individual_averaged.missing_value
		self.individual_averaged=Individual_averaged(self.line, 'female')
		self.assertEqual(self.missing_value, '-')

	def test_minimal(self):
		self.individual_averaged.add(self.line)

class test_num_sigfigs(unittest.TestCase):
	'''Technically not a function of Individual_averaged class, but heavily used by it'''
	def test_values_greater_than_or_equal_to_1(self):
		self.assertEqual(num_sigfigs('1.5'), 2)
		self.assertEqual(num_sigfigs('2'), 1)
		self.assertEqual(num_sigfigs('-3'), 1)
		self.assertEqual(num_sigfigs('05'), 1)
		self.assertEqual(num_sigfigs('1.001'), 4)
		self.assertEqual(num_sigfigs('1.00'), 3)
		self.assertEqual(num_sigfigs('100'), 1)
		self.assertEqual(num_sigfigs('100.'), 3)

	def test_values_less_than_1(self):
		self.assertEqual(num_sigfigs('0'), 1)
		self.assertEqual(num_sigfigs('0.0'), 1)
		self.assertEqual(num_sigfigs('.5'), 1)
		self.assertEqual(num_sigfigs('0.5'), 1)
		self.assertEqual(num_sigfigs('0.000243'), 3)
		self.assertEqual(num_sigfigs('.00003'), 1)

	def test_scientific_notation(self):
		self.assertEqual(num_sigfigs('05.5+1'), 2)
		self.assertEqual(num_sigfigs('3E+5'), 1)
		self.assertEqual(num_sigfigs('5E-7'), 1)
		self.assertEqual(num_sigfigs('5.34E-7'), 3)
		self.assertEqual(num_sigfigs('05.34E-7'), 3)
		self.assertEqual(num_sigfigs('-05.34E-7'), 3)

class test_average_round_min(unittest.TestCase):
	def setUp(self):
		Individual_averaged.rounding_method_for_averaging=round.min
		self.line=['iid','strain','male']
		self.individual_averaged=Individual_averaged(self.line, 'female')

	def assertAvgEqual(self, values_to_average, true_avg):
		self.assertEqual(self.individual_averaged.average(values_to_average), true_avg)

	def assertAvgNotEqual(self, values_to_average, true_avg):
		self.assertNotEqual(self.individual_averaged.average(values_to_average), true_avg)

	def test_single_value(self):
		self.assertAvgEqual(['23.3'], '23.3')	# sum= 23.3, sf=1, avg=24.3
		self.assertAvgEqual(['.3'], '0.3')		# sum= 0.3, sf=1, avg=24.3
		self.assertAvgEqual(['-.3'], '-0.3')	# sum= -0.3, sf=1, avg=24.3
		self.assertAvgEqual(['-0.3'], '-0.3')	# sum= -0.3, sf=1, avg=24.3

	def test_scientific_notation(self):
		self.assertAvgEqual(['23.3','3','46.6'], '2E+1')		# sum= , sf=1, avg=24.3
		self.assertAvgEqual(['-23.3','-3','-46.6'], '-2E+1')	# sum= , sf=1, avg=24.3
		self.assertAvgEqual(['.000233','.00003','.000466'], '0.0002')	# sum= , sf=1, avg=0.000243
		self.assertAvgEqual(['-.000233','-.000030','-.000466'], '-0.00024')	# sum= , sf=2, avg=0.000243

	def test_decimal_values(self):
		self.assertAvgEqual(['.233','.03','.466'], '0.2')	# sum= , sf=1, avg=24.3
		self.assertAvgEqual(['-.233','-.03','-.466'], '-0.2')	# sum= , sf=1, avg=24.3
		self.assertAvgEqual(['.0233','.003','.0466'], '0.02')	# sum= , sf=5, avg=24.3
		self.assertAvgEqual(['.55','.95','.85'], '0.78') # sum=2.35, sf=2, avg=0.78333...
		self.assertAvgEqual(['.05','-.95','.85'], '-0.02') # sum=0.05, sf=1, avg=-0.01666...

	def test_sigfigs_of_positive_values(self):
		self.assertAvgEqual(['2.55','1'], '2')		# sum= , sf=1, avg=1.775
		self.assertAvgEqual(['2.55','1.0'], '1.8')	# sum= , sf=2, avg=1.775
		self.assertAvgEqual(['2.55','1.00'], '1.78')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.55','1.000'], '1.78')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.550','1.000'], '1.775')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.55','2.55'], '2.55')	# sum= , sf=2, avg=1.775
		self.assertAvgEqual(['49.7','50.2','50'], '5E+1')	# sum= , sf=1, avg=49.9666...

	def test_sigfigs_of_negative_values(self):
		self.assertAvgEqual(['-2.55','-1'], '-2')		# sum= , sf=1, avg=1.775
		self.assertAvgEqual(['-2.55','-1.0'], '-1.8')	# sum= , sf=2, avg=1.775
		self.assertAvgEqual(['-2.55','-1.00'], '-1.78')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['-2.55','-1.000'], '-1.78')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['-2.550','-1.000'], '-1.775')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['-2.55','-2.55'], '-2.55')	# sum= , sf=2, avg=1.775

	def test_leading_and_trailing_zeroes(self):
		self.assertAvgEqual(['02.55','1'], '2')		# sum= , sf=1, avg=1.775
		self.assertAvgEqual(['2.5500','1.0'], '1.8')	# sum= , sf=2, avg=1.775
		self.assertAvgEqual(['02.55','01.00'], '1.78')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.5500','1.00'], '1.78')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.550','1.00000'], '1.775')	# sum= , sf=4, avg=1.775
		self.assertAvgEqual(['2.5500','02.55'], '2.55')	# sum= , sf=3, avg=1.775

	def test_round_even_with_5(self):
		# check that a 5 rounds last significant digit up if that digit is odd,
		# but does merely truncates everything after that digit if it's even
		self.assertAvgEqual(['3.5','2.0','2.15'], '2.6')	# sum= , sf=2, avg=2.55
		self.assertAvgEqual(['3.5','2.0','2.45'], '2.6')	# sum= , sf=2, avg=2.65
		values=['-']

	def test_missing_value(self):
		self.assertAvgEqual([self.individual_averaged.missing_value],
			self.individual_averaged.missing_value)



class test_average_round_max(unittest.TestCase):
	def setUp(self):
		Individual_averaged.rounding_method_for_averaging=round.max
		self.line=['iid','strain','male']
		self.individual_averaged=Individual_averaged(self.line, 'female')

	def assertAvgEqual(self, values_to_average, true_avg):
		self.assertEqual(self.individual_averaged.average(values_to_average), true_avg)

	def assertAvgNotEqual(self, values_to_average, true_avg):
		self.assertNotEqual(self.individual_averaged.average(values_to_average), true_avg)

	def test_single_value(self):
		self.assertAvgEqual(['23.3'], '23.3')		# sum= , sf=1, avg=24.3
		self.assertAvgEqual(['.3'], '0.3')		# sum= , sf=1, avg=24.3
		self.assertAvgEqual(['-.3'], '-0.3')		# sum= , sf=1, avg=24.3
		self.assertAvgEqual(['-0.3'], '-0.3')		# sum= , sf=1, avg=24.3

	def test_scientific_notation(self):
		self.assertAvgEqual(['23.3','3','46.6'], '24.3')		# sum= , sf=1, avg=24.3
		self.assertAvgEqual(['-23.3','-3','-46.6'], '-24.3')	# sum= , sf=1, avg=24.3
		self.assertAvgEqual(['.000233','.00003','.000466'], '0.000243')	# sum= , sf=1, avg=0.000243
		self.assertAvgEqual(['-.000233','-.000030','-.000466'], '-0.000243')	# sum= , sf=2, avg=0.000243

	def test_decimal_values(self):
		self.assertAvgEqual(['.233','.03','.466'], '0.243')	# sum= , sf=1, avg=0.243
		self.assertAvgEqual(['-.233','-.03','-.466'], '-0.243')	# sum= , sf=1, avg=-0.243
		self.assertAvgEqual(['.0233','.003','.0466'], '0.0243')	# sum= , sf=5, avg=0.0243
		self.assertAvgEqual(['.55','.95','.85'], '0.783') # sum=2.35, sf=2, avg=0.78333...
		self.assertAvgEqual(['.05','-.95','.85'], '-0.02') # sum=0.05, sf=1, avg=-0.01666...

	def test_sigfigs_of_positive_values(self):
		self.assertAvgEqual(['2.55','1'], '1.78')		# sum= , sf=1, avg=1.775
		self.assertAvgEqual(['2.55','1.0'], '1.78')	# sum= , sf=2, avg=1.775
		self.assertAvgEqual(['2.55','1.00'], '1.78')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.55','1.000'], '1.775')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.550','1.000'], '1.775')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.55','2.55'], '2.55')	# sum= , sf=2, avg=1.775
		self.assertAvgEqual(['49.7','50.2','50'], '49.97') # sum=149.9, sf=4, avg=49.966...

	def test_sigfigs_of_negative_values(self):
		self.assertAvgEqual(['-2.55','-1'], '-1.78')		# sum= , sf=1, avg=1.775
		self.assertAvgEqual(['-2.55','-1.0'], '-1.78')	# sum= , sf=2, avg=1.775
		self.assertAvgEqual(['-2.55','-1.00'], '-1.78')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['-2.55','-1.000'], '-1.775')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['-2.550','-1.000'], '-1.775')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['-2.55','-2.55'], '-2.55')	# sum= , sf=2, avg=1.775

	def test_leading_and_trailing_zeroes(self):
		self.assertAvgEqual(['02.55','1'], '1.78')		# sum= , sf=1, avg=1.775
		self.assertAvgEqual(['2.5500','1.0'], '1.7750')	# sum= , sf=2, avg=1.775
		self.assertAvgEqual(['02.55','01.00'], '1.78')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.5500','1.00'], '1.7750')	# sum= , sf=3, avg=1.775
		self.assertAvgEqual(['2.550','1.00000'], '1.77500')	# sum= , sf=4, avg=1.775
		self.assertAvgEqual(['2.5500','02.55'], '2.5500')	# sum= , sf=3, avg=1.775

	def test_round_even_with_5(self):
		values=['-']

	def test_missing_value(self):
		self.assertAvgEqual([self.individual_averaged.missing_value],
			self.individual_averaged.missing_value)


#
# if __name__ == '__main__':
# 	suite_names=[test__init__, test_add, test_num_sigfigs, test_average]
# 	all_suites=[]
# 	for suite_name in suite_names:
# 		suites.add(unittest.TestLoader().loadTestsFromTestCase(suite_name))
# 	all_tests=unittest.TestSuite(all_suites)
# 	unittest.TextTestRunner(verbosity=2).run(all_tests)
