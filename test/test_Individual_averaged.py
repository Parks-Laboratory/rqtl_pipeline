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
		
		
class test_add(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male']
		self.individual_averaged = Individual_averaged(self.line, 'female')
		
	def test_minimal(self):
		self.individual_averaged.add(self.line)
			
			
			
# class test_average(unittest.TestCase):
			
			
if __name__ == '__main__':
	suite_names = [test__init__, test_add, test_average]
	all_suites = []
	for suite_name in suite_names:
		suites.add(unittest.TestLoader().loadTestsFromTestCase(suite_name))
	all_tests = unittest.TestSuite(all_suites)
	unittest.TextTestRunner(verbosity=2).run(all_tests)

	