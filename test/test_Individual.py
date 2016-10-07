from src.makeRQTLInputs import *
import unittest

class test__init__(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male']

	def test_minimal(self):
		self.individual = Individual(self.line)


class test_add(unittest.TestCase):
	def setUp(self):
		self.line = ['iid','strain','male']
		self.individual = Individual(self.line)

	def test_minimal(self):
		self.individual.add(self.line)


class test_replace_missing_value(unittest.TestCase):
	def setUp(self):
		self.numeric_values = ['9', '5.4', '0.324467854359405348505345',
			'-234', '-.7546', '3444234324897987297894', '3e+4', '6e-16']
		self.non_numeric_values = ['-','23 34', '34%', '[3243]', '{34}', '23..3',
			'5/6']

	def test_non_numeric_values(self):
		for value in self.non_numeric_values:
			self.assertEqual(Individual.missing_value, Individual.replace_missing_value(value) )


	def test_numeric_values(self):
		for value in self.numeric_values:
			self.assertEqual(value, Individual.replace_missing_value(value) )


if __name__ == '__main__':
	suite_names = [test__init__, test_add, test_replace_missing_value]
	all_suites = []
	for suite_name in suite_names:
		suites.add(unittest.TestLoader().loadTestsFromTestCase(suite_name))
	all_tests = unittest.TestSuite(all_suites)
	unittest.TextTestRunner(verbosity=2).run(all_tests)
