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
		self.line = ['iid','strain','male']
		self.individual_averaged = Individual_averaged(self.line, 'female')
		
	def test_minimal(self):
		self.individual_averaged.add(self.line)
					

class test_round_sigfigs(unittest.TestCase):
	def setUp(self):
		self.valid_values = [3434, 343, 343.3, 34, -34, .34, -.34, 
			.32437932478327, 39723324]
		self.invalid_values = []
	
	def test_valid_values(self):
		for value in self.valid_values:
			self.assertTrue( is_numeric( round_sigfigs(value, 3) ) )
		
	# def test_invalid_values(self):
		
					
class test_average(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male']
		self.individual_averaged = Individual_averaged(self.line, 'female')

	def test(self):
		values = ['23.3','3','46.6']
		self.assertIsNotNone(self.individual_averaged.average(values))

		
			
if __name__ == '__main__':
	suite_names = [test__init__, test_add, test_average]
	all_suites = []
	for suite_name in suite_names:
		suites.add(unittest.TestLoader().loadTestsFromTestCase(suite_name))
	all_tests = unittest.TestSuite(all_suites)
	unittest.TextTestRunner(verbosity=2).run(all_tests)

	