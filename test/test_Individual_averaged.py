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


class test_average(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male']
		self.individual_averaged = Individual_averaged(self.line, 'female')

	def assertAvgEqual(self, values_to_average, true_avg):
		self.assertEqual(self.individual_averaged.average(values_to_average), true_avg)

	def assertAvgNotEqual(self, values_to_average, true_avg):
		self.assertNotEqual(self.individual_averaged.average(values_to_average), true_avg)

	def test_scientific_notation(self):
		# average = 24.3
		self.assertAvgEqual(['23.3','3','46.6'], '2E+1')

	def test_sigfigs_of_positive_values(self):
		self.assertAvgEqual(['2.55','1'], '2')		# avg = 1.775, sigfigs = 1
		self.assertAvgEqual(['2.55','1.0'], '1.8')	# avg = 1.775, sigfigs = 2
		self.assertAvgEqual(['2.55','1.00'], '1.78')	# avg = 1.775, sigfigs = 3
		self.assertAvgEqual(['2.55','1.000'], '1.78')	# avg = 1.775, sigfigs = 3
		self.assertAvgEqual(['2.550','1.000'], '1.775')	# avg = 1.775, sigfigs = 3
		self.assertAvgEqual(['2.55','2.55'], '2.55')	# avg = 1.775, sigfigs = 2

	def test_sigfigs_of_negative_values(self):
		self.assertAvgEqual(['-2.55','-1'], '-2')		# avg = 1.775, sigfigs = 1
		self.assertAvgEqual(['-2.55','-1.0'], '-1.8')	# avg = 1.775, sigfigs = 2
		self.assertAvgEqual(['-2.55','-1.00'], '-1.78')	# avg = 1.775, sigfigs = 3
		self.assertAvgEqual(['-2.55','-1.000'], '-1.78')	# avg = 1.775, sigfigs = 3
		self.assertAvgEqual(['-2.550','-1.000'], '-1.775')	# avg = 1.775, sigfigs = 3
		self.assertAvgEqual(['-2.55','-2.55'], '-2.55')	# avg = 1.775, sigfigs = 2


	def test_round_even_with_5(self):
		# check that a 5 rounds last significant digit up if that digit is odd,
		# but does merely truncates everything after that digit if it's even
		self.assertAvgEqual(['3.5','2.0','2.15'], '2.6')	# avg = 2.55, sigfigs = 2
		self.assertAvgEqual(['3.5','2.0','2.45'], '2.6')	# avg = 2.65, sigfigs = 2
		values = ['-']




if __name__ == '__main__':
	suite_names = [test__init__, test_add, test_average]
	all_suites = []
	for suite_name in suite_names:
		suites.add(unittest.TestLoader().loadTestsFromTestCase(suite_name))
	all_tests = unittest.TestSuite(all_suites)
	unittest.TextTestRunner(verbosity=2).run(all_tests)
