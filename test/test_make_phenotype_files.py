from src.makeRQTLInputs import *
import unittest
import io
from testfixtures import tempdir, compare	# easier setup/cleanup test output
'''
TODO:
	-Make simple phenotypes.csv for classes in this file to read in
		-Entries should be chosen so that the correct file
		will only match the generated file if makeRQTLInputs.py is correct
		-Input file entries also contain all legal types of values
		(i.e. positive/negative integers/decimals, NA, missing values)
'''

inputFile = '''Mouse ID,Strain,Sex,Weight-0 wks diet,AVG Food Intake - 4 Wks Diet,Trigly. ,Esterified Chol,Liver/NMR_Mass_8wks
	OB-642,BXD1/TyJ,Male,26.13,1.916,26,135,0.034937672
	OB-643,BXD1/TyJ,Male,24.3,1.916,,NA,0.032453926
	OB-644,BXD1/TyJ,Male,26.02,1.916,,NA,0.031792949
	OB-645,BXD1/TyJ,Female,17.5,1.796666667,,-51,0.037768186
	OB-646,BXD1/TyJ,Female,16.8,1.796666667,,-71,0.04374075
	OB-647,BXD1/TyJ,Female,21.03,1.796666667,21,119,0.038343416
	OB-794,BXD11/TyJ,Male,21.8,NA,,NA,NA
	OB-795,BXD11/TyJ,Male,22.77,NA,42,116,0.026576982
	OB-847,BXD11/TyJ,Male,23.4,4.418,78,110,0.035573502
	OB-848,BXD11/TyJ,Male,21.89,4.418,47,105,0.029217737
	OB-125,BXD27/TyJ,Female,20.76,3.367,45.3125,223.4375,0.03878796
	OB-126,BXD27/TyJ,Female,19.5,3.367,26.5625,159.375,0.031361702
	OB-127,BXD27/TyJ,Female,19.76,3.367,20.3125,118.75,0.030875435
	OB-638,BXD27/TyJ,Female,19.66,3.4,22,246,0.034066768
	OB-639,BXD27/TyJ,Female,21.76,3.4,28,254,0.04117155
	OB-640,BXD27/TyJ,Female,19.39,3.4,33,201,0.031396196
	OB-641,BXD27/TyJ,Female,17.51,3.4,21,196,0.031466593'''

inputLines = [line.strip().split(',') for line in inputFile]

def examine_dir(dir):
	'''Pauses execution to allow examinatino of temporary directory'''
	print(dir.path)
	print('Press "y" to continue execution.')
	cmd = 'n'
	while(cmd != 'y'):
		cmd = input()


class test_make_phenotype_files_average(unittest.TestCase):
	'''
	Test goals:
		-Need to make sure that output file averages were derived from
		the correct group (Strain then Sex) in input file
		-Don't need to test rounding or scientific notation
		b/c other test classes exist to check for that
	'''

	@tempdir()
	@classmethod
	def setUpClass(cls, dir):
		print(cls.dir.path)

	@tempdir()
	def test_hetro(self, dir):
		'''-use File.readlines() to get next string of each file
		and assert that they are equal
		-TODO decide what test should do'''

		# python appends \n to ever line, so for comparing on windows add \r to make \r\n
		correct_output ='''Weight_0_wks_diet,18.44,25.48,-,22.46,19.763,-
AVG_Food_Intake_4_Wks_Diet,1.796666667,1.916,-,4.418,3.3859,-
Trigly,21,26,-,55.7,28.02679,-
Esterified_Chol,-1,135,-,110,199.79464,-
Liver_NMR_Mass_8wks,0.039950784,0.033061516,-,0.030456074,0.0341608863,-
sex,0,1,0,1,0,1
id,BXD1_TyJ.f,BXD1_TyJ.m,BXD11_TyJ.f,BXD11_TyJ.m,BXD27_TyJ.f,BXD27_TyJ.m
'''
		correct_output = correct_output.replace('\n', os.linesep)


		Global.output_dir = dir.path	# set global variable in makeRQTLInputs
		input = io.StringIO(inputFile)
		pheno_lines = [line.strip().split(',') for line in input]
		input.close()
		# file = open('test.txt', 'utf-8')
		# dir.write('test.txt', inputFile, 'utf-8')
		# file = open(os.path.join(output_dir,'test.txt'))
		# linesFromString = [line.strip().split(',') for line in inputFile]
		use_average_by_strain = True
		output_filename = File_builder.build_filename(
			Parameter.PHENO_FILENAME_PREFIXES[Global.HETERO],
			Parameter.PHENO_FILENAME_SUFFIX )

		make_phenotype_files(pheno_lines, Parameter.PHENO_FILENAME_SUFFIX, use_average_by_strain)
		output = dir.read(output_filename, 'utf-8')
		# examine_dir(dir)
		# self.assertMultiLineEqual(output, correct_output)
		# compare(dir.read(output_filename, 'utf-8'), correctOutputFile)
		self.maxDiff = None  # display comparisons of all lines
		self.assertMultiLineEqual(output, correct_output)


	# @classmethod
	# def tearDownClass(cls):
	# 	self.dir.cleanup()

@unittest.skip("not done")
class test_make_phenotype_files_not_averaged(unittest.TestCase):
	# @classmethod
	# def setUpClass(cls):

	def test(self):
		correct_outputFile ='''Weight_0_wks_diet,26.13,24.3,26.02,17.5,16.8,21.03,21.8,22.77,23.4,21.89,20.76,19.5,19.76,19.66,21.76,19.39,17.51
AVG_Food_Intake_4_Wks_Diet,1.916,1.916,1.916,1.796666667,1.796666667,1.796666667,-,-,4.418,4.418,3.367,3.367,3.367,3.4,3.4,3.4,3.4
Trigly,26,-,-,-,-,21,-,42,78,47,45.3125,26.5625,20.3125,22,28,33,21
Esterified_Chol,135,-,-,-51,-71,119,-,116,110,105,223.4375,159.375,118.75,246,254,201,196
Liver_NMR_Mass_8wks,0.034937672,0.032453926,0.031792949,0.037768186,0.04374075,0.038343416,-,0.026576982,0.035573502,0.029217737,0.03878796,0.031361702,0.030875435,0.034066768,0.04117155,0.031396196,0.031466593
sex,1,1,1,0,0,0,1,1,1,1,0,0,0,0,0,0,0
id,OB_642,OB_643,OB_644,OB_645,OB_646,OB_647,OB_794,OB_795,OB_847,OB_848,OB_125,OB_126,OB_127,OB_638,OB_639,OB_640,OB_641
'''
		# TODO decide what test should do
		self.assertTrue(True)
