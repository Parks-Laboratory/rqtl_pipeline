from src.get_rqtl import *
import unittest

female_sex_index = sex_label_as_numeric[female]
male_sex_index = sex_label_as_numeric[male]

class test_averaged(unittest.TestCase):
	def test_append_simple(self):
		strains = Strains(True)
		iid = 'Jake'
		strain = 'Husky'
		sex = 'male'
		male_sex_index = sex_label_as_numeric[sex]
		self.line = [iid, strain, sex]
		strains.append(self.line)
		self.assertEqual(strains.strains[strain][male_sex_index].sex, male_sex_index)
		self.assertEqual(strains.strains[strain][male_sex_index].strain, strain)
		self.assertEqual(strains.strains[strain][male_sex_index].rows[0], male_sex_index)
		self.assertEqual(strains.strains[strain][male_sex_index].rows[1], 'Husky.m')

	def test_append(self):
		strains = Strains(True)
		# add male husky, do basic tests
		strain = 'Husky'
		self.line = ['Jake', strain, male, '-', '0', '1', '2', '4', '8']
		strains.append(self.line)
		male_husky = strains.strains[strain][male_sex_index]
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
		strains.append(['Franco', strain, male, '0', '-', '1', '2', '6', '3'])
		strains.append(['Sam', strain, male, '2', '-', '1', '-', '7', '5'])
		self.assertEqual(male_husky.rows, [['0','2'], ['0'], ['1','1','1'], ['2','2'],
			['4','6','7'], ['8','3','5'], male_sex_index, 'Husky.m'])

		# add female huskies, make sure data stored correctly
		female_husky = strains.strains[strain][female_sex_index]
		strains.append(['Ellie', strain, female, '-', '-', '-', '2.2', '.6', '-'])
		strains.append(['Nancy', strain, female, '3.0', '-', '1.1', '-', '7', '2'])
		strains.append(['Irene', strain, female, '3.2E-1', '-', '-', '7', '.7', '1'])
		self.assertEqual(female_husky.rows, [['3.0','3.2E-1'], '-', ['1.1'], ['2.2','7'],
		['.6','7','.7'], ['2','1'], female_sex_index, 'Husky.f'])

		# add another strain, make sure data stored correctly for that strain
		strain = 'Main_Coon'
		strains.append(['Franco', strain, male, '0', '-', '1', '2', '6', '3'])
		strains.append(['Nancy', strain, female, '3.0', '-', '1.1', '-', '7', '2'])
		female_main_coon = strains.strains[strain][female_sex_index]
		male_main_coon = strains.strains[strain][male_sex_index]
		self.assertEqual(male_main_coon.rows, [['0'], '-', ['1'], ['2'],
			['6'], ['3'], male_sex_index, 'Main_Coon.m'])
		self.assertEqual(female_main_coon.rows, [['3.0'], '-', ['1.1'], '-',
			['7'], ['2'], female_sex_index, 'Main_Coon.f'])

		# add an individual to huskies w/ no data, make sure nothing changes
		strain = 'Husky'
		strains.append(['Ellie', strain, female, '-', '-', '-', '-', '-', '-'])
		strains.append(['Sam', strain, male, '-', '-', '-', '-', '-', '-'])
		self.assertEqual(female_husky.rows, [['3.0','3.2E-1'], '-', ['1.1'], ['2.2','7'],
			['.6','7','.7'], ['2','1'], female_sex_index, 'Husky.f'])
		self.assertEqual(female_husky.rows, [['3.0','3.2E-1'], '-', ['1.1'], ['2.2','7'],
			['.6','7','.7'], ['2','1'], female_sex_index, 'Husky.f'])

class test_not_averaged(unittest.TestCase):
	def verify(self, individual_rows, correct_rows):
		'''Iterate over all an individual's phenotypes and make sure they are
		the same as the ones with which it was created'''
		correct_rows = (correct_rows[Individual.first_phenotype_column_index:]+
						[sex_label_as_numeric[correct_rows[Individual.sex_column_index]]] +
						[correct_rows[Individual.iid_column_index]])
		for index, phenotype in enumerate(individual_rows):
			self.assertEqual(individual_rows[index], correct_rows[index])

	def test_append(self):
		# add individual, check fields
		strains = Strains(False)
		iid = 'Jake'
		strain = 'Husky'
		sex = 'male'
		male_sex_index = sex_label_as_numeric[sex]
		jake_line = [iid, strain, sex, '-', '0', '1', '2', '4', '8']
		strains.append(jake_line)
		jake = strains.strains[strain][0]
		self.assertEqual(jake.rows, ['-', '0', '1', '2', '4', '8',male_sex_index,iid])
		self.assertEqual(jake.sex, male_sex_index)
		self.assertEqual(jake.strain, strain)
		self.verify(jake.rows, jake_line)

		# add 2 more male huskies, make sure data stored correctly
		franco_line = ['Franco', strain, male, '0', '-', '1', '2', '6', '3']
		sam_line = ['Sam', strain, male, '2', '-', '1', '-', '7', '5']
		strains.append(franco_line)
		strains.append(sam_line)
		franco = strains.strains[strain][1]
		sam = strains.strains[strain][2]
		self.verify(franco.rows, franco_line)
		self.verify(sam.rows, sam_line)

		# add female huskies, make sure data stored correctly
		ellie_line = ['Ellie', strain, female, '-', '-', '-', '2.2', '.6', '-']
		nancy_line = ['Nancy', strain, female, '3.0', '-', '1.1', '-', '7', '2']
		irene_line = ['Irene', strain, female, '3.2E-1', '-', '-', '7', '.7', '1']
		strains.append(ellie_line)
		strains.append(nancy_line)
		strains.append(irene_line)
		ellie = strains.strains[strain][3]
		nancy = strains.strains[strain][4]
		irene = strains.strains[strain][5]
		self.verify(ellie.rows, ellie_line)
		self.verify(nancy.rows, nancy_line)
		self.verify(irene.rows, irene_line)

		# add another strain, make sure data stored correctly for that strain
		strain = 'Main_Coon'
		jacen_line = ['Jacen', strain, male, '0', '-', '1', '2', '6', '3']
		jaina_line = ['Jaina', strain, female, '3.0', '-', '1.1', '-', '7', '2']
		strains.append(jacen_line)
		strains.append(jaina_line)
		jacen = strains.strains[strain][0]
		jaina = strains.strains[strain][1]
		self.verify(jacen.rows, jacen_line)
		self.verify(jaina.rows, jaina_line)

		# add an individual to huskies w/ no data, make sure nothing gets overwritten
		strain = 'Husky'
		ellie_2_line = ['Ellie', strain, female, '-', '-', '-', '-', '-', '-']
		sam_2_line = ['Sam', strain, male, '-', '-', '-', '-', '-', '-']
		strains.append(ellie_2_line)
		strains.append(sam_2_line)
		ellie_2 = strains.strains[strain][6]
		sam_2 = strains.strains[strain][7]
		self.verify(ellie.rows, ellie_line)
		self.verify(sam.rows, sam_line)

		# verify it all again
		self.verify(jacen.rows, jacen_line)
		self.verify(jaina.rows, jaina_line)
		self.verify(ellie.rows, ellie_line)
		self.verify(nancy.rows, nancy_line)
		self.verify(irene.rows, irene_line)
		self.verify(franco.rows, franco_line)
		self.verify(sam.rows, sam_line)
		self.verify(jake.rows, jake_line)



#
# if __name__ == '__main__':
# 	suite_names = [test_]
# 	all_suites = []
# 	for suite_name in suite_names:
# 		suites.add(unittest.TestLoader().loadTestsFromTestCase(suite_name))
# 	all_tests = unittest.TestSuite(all_suites)
# 	unittest.TextTestRunner(verbosity=2).run(all_tests)
