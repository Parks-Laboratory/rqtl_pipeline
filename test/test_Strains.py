from src.get_rqtl import *
import unittest

female_sex_index = sex_label_as_numeric[female]
male_sex_index = sex_label_as_numeric[male]

class test_averaged(unittest.TestCase):
	def test_append_simple(self):
		self.strains = Strains(True)
		iid = 'Jake'
		strain = 'Husky'
		sex = 'male'
		male_sex_index = sex_label_as_numeric[sex]
		self.line = [iid, strain, sex]
		self.strains.append(self.line)
		self.assertEqual(self.strains.strains[strain][male_sex_index].sex, male_sex_index)
		self.assertEqual(self.strains.strains[strain][male_sex_index].strain, strain)
		self.assertEqual(self.strains.strains[strain][male_sex_index].rows[0], male_sex_index)
		self.assertEqual(self.strains.strains[strain][male_sex_index].rows[1], 'Husky.m')

	def test_append(self):
		self.strains = Strains(True)
		# add male husky, do basic tests
		strain = 'Husky'
		self.line = ['Jake', strain, male, '-', '0', '1', '2', '4', '8']
		self.strains.append(self.line)
		male_husky = self.strains.strains[strain][male_sex_index]
		self.assertEqual(male_husky.rows, ['-', ['0'], ['1'], ['2'], ['4'], ['8'],male_sex_index,'Husky.m'])
		self.assertEqual(male_husky.sex, male_sex_index)
		self.assertEqual(male_husky.strain, strain)
		# each non-missing value is part of a list of values that will be averaged
		for index, phenotype in enumerate(self.line[3:]):
			if phenotype == Individual.missing_value:
				self.assertEqual(male_husky.rows[index], self.line[3+index])
			else:
				self.assertEqual(male_husky.rows[index], [self.line[3+index]])

		# add 2 more male huskies, make sure data stored correctly
		self.strains.append(['Franco', strain, male, '0', '-', '1', '2', '6', '3'])
		self.strains.append(['Sam', strain, male, '2', '-', '1', '-', '7', '5'])
		self.assertEqual(male_husky.rows, [['0','2'], ['0'], ['1','1','1'], ['2','2'],
			['4','6','7'], ['8','3','5'], male_sex_index, 'Husky.m'])

		# add female huskies, make sure data stored correctly
		female_husky = self.strains.strains[strain][female_sex_index]
		self.strains.append(['Ellie', strain, female, '-', '-', '-', '2.2', '.6', '-'])
		self.strains.append(['Nancy', strain, female, '3.0', '-', '1.1', '-', '7', '2'])
		self.strains.append(['Irene', strain, female, '3.2E-1', '-', '-', '7', '.7', '1'])
		self.assertEqual(female_husky.rows, [['3.0','3.2E-1'], '-', ['1.1'], ['2.2','7'],
		['.6','7','.7'], ['2','1'], female_sex_index, 'Husky.f'])

		# add another strain, make sure data stored correctly for that strain
		strain = 'Main_Coon'
		self.strains.append(['Franco', strain, male, '0', '-', '1', '2', '6', '3'])
		self.strains.append(['Nancy', strain, female, '3.0', '-', '1.1', '-', '7', '2'])
		female_main_coon = self.strains.strains[strain][female_sex_index]
		male_main_coon = self.strains.strains[strain][male_sex_index]
		self.assertEqual(male_main_coon.rows, [['0'], '-', ['1'], ['2'],
			['6'], ['3'], male_sex_index, 'Main_Coon.m'])
		self.assertEqual(female_main_coon.rows, [['3.0'], '-', ['1.1'], '-',
			['7'], ['2'], female_sex_index, 'Main_Coon.f'])

		# add an individual to huskies w/ no data, make sure nothing changes
		self.strains.append(['Ellie', strain, female, '-', '-', '-', '-', '-', '-'])
		self.strains.append(['Sam', strain, male, '-', '-', '-', '-', '-', '-'])
		self.assertEqual(female_husky.rows, [['3.0','3.2E-1'], '-', ['1.1'], ['2.2','7'],
			['.6','7','.7'], ['2','1'], female_sex_index, 'Husky.f'])
		self.assertEqual(female_husky.rows, [['3.0','3.2E-1'], '-', ['1.1'], ['2.2','7'],
			['.6','7','.7'], ['2','1'], female_sex_index, 'Husky.f'])

class test_not_averaged(unittest.TestCase):
	def test_append(self):
		self.strains = Strains(False)
		iid = 'Jake'
		strain = 'Husky'
		sex = 'male'
		male_sex_index = sex_label_as_numeric[sex]
		self.line = [iid, strain, sex, '-', '0', '1', '2', '4', '8']
		self.strains.append(self.line)
		male_husky = self.strains.strains[strain][0]
		self.assertEqual(male_husky.rows, ['-', '0', '1', '2', '4', '8',male_sex_index,iid])
		self.assertEqual(male_husky.sex, male_sex_index)
		self.assertEqual(male_husky.strain, strain)
		for index, phenotype in enumerate(self.line[3:]):
			self.assertEqual(male_husky.rows[index], self.line[3+index])





#
# if __name__ == '__main__':
# 	suite_names = [test_]
# 	all_suites = []
# 	for suite_name in suite_names:
# 		suites.add(unittest.TestLoader().loadTestsFromTestCase(suite_name))
# 	all_tests = unittest.TestSuite(all_suites)
# 	unittest.TextTestRunner(verbosity=2).run(all_tests)
