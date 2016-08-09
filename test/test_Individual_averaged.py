from src.get_rqtl import *
import unittest

class test__init__(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male']
	
	def test_normal__init__(self):
		self.individual = Individual(self.line)

		
class test_add(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male']
		self.individual = Individual(self.line)
		
	def test_add(self):
		self.individual.add(self.line)
	
	
if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(test__init__)
	unittest.TextTestRunner(verbosity=2).run(suite)
    # unittest.main()	
	
# individ_test_case = test_Individual_averaged('Test_replace_missing_value')	


# individ_test_suite = TestSuite()
# individ_test_suite.addTest()	

	