from src.make_rqtl_inputs import *
import unittest  # use @unittest.skip("some message") to skip a test
import io
import pdb  # use pdb.set_trace() to start Python debugger at a certain line
from testfixtures import TempDirectory, tempdir, compare	# easier setup/cleanup test output

def examine_dir(dir):
	'''Pauses execution to allow examination of temporary directory'''
	print('Temporary dir.:',dir.path)
	print('Press "y" to continue execution.')
	cmd = 'n'
	while(cmd != 'y'):
		cmd = input()


geno_file = '''rs29270490
rs50906391
rs29588301
rs29568258
rs27034352
rs36773429
rs31196255
rs32595055
rs6262668
rs6196410
'''


pheno_file = '''Mouse ID,Strain,Sex,Weight-0 wks diet,AVG Food Intake - 4 Wks Diet,Trigly. ,Esterified Chol,Liver/NMR_Mass_8wks
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


class geno_test(unittest.TestCase):
	'''Set-up functionality required for test-classes in this file'''
	def buildFiles(cls, use_average_by_strain):
		Geno_file_builder.reset()
		dir = TempDirectory()
		cls.dir = dir
		Global.output_dir = dir.path	# set global variable in makeRQTLInputs

		# Get info from make_phenotype_files
		pheno_input = io.StringIO(pheno_file)
		pheno_lines = [line.strip().split(',') for line in pheno_input]
		pheno_input.close()
		phenotype_data_by_strain = make_phenotype_files(pheno_lines, use_average_by_strain)

		geno_input = io.StringIO(geno_file)
		geno_lines = [line.strip().split('\t') for line in geno_input if line.strip()]
		geno_input.close()
		# Convert marker lines to strings
		markers = set()
		for line in geno_lines:
			markers.add(Global.EMPTY_STRING.join(line))

		make_genotype_files( phenotype_data_by_strain, markers )


	def compareFiles(self, cls, correct_output):
		correct_output = correct_output.replace('\n', os.linesep)

		output_filename = File_builder.build_filename(
			Parameter.MAIN_GENO_FILENAME_PREFIX,
			Parameter.GENO_FILENAME_SUFFIX )

		output = cls.dir.read(output_filename, 'utf-8')

		# examine_dir(cls.dir)
		self.maxDiff = None  # display comparisons of all lines
		self.assertMultiLineEqual(output, correct_output)

	@classmethod
	def tearDownClass(cls):
		TempDirectory.cleanup_all()


class test_make_genotype_files_average(geno_test):
	'''Test that genotype file has 2 columns of identical genotype data for each
	strain; the first for the females, and the second for the males'''
	@classmethod
	def setUpClass(cls):
		super().buildFiles(cls, True)

	def test_average(self):
		correct_output = '''id,,,BXD1_TyJ.f,BXD1_TyJ.m,BXD11_TyJ.f,BXD11_TyJ.m,BXD27_TyJ.f,BXD27_TyJ.m
rs6196410,1,33.7580975,A,A,A,A,B,B
rs27034352,11,54.085187,B,B,A,A,A,A
rs29588301,13,44.7742875,B,B,B,B,B,B
rs29568258,13,45.250384,B,B,B,B,H,H
rs50906391,16,22.8040365,A,A,B,B,B,B
rs6262668,3,75.764573,B,B,B,B,B,B
rs32595055,5,17.9862455,A,A,B,B,A,A
rs31196255,7,57.8978535,A,A,A,A,A,A
rs36773429,9,42.7108535,B,B,A,A,A,A
rs29270490,X,66.918496,A,A,A,A,B,B
'''
		super().compareFiles(type(self), correct_output)


class test_make_genotype_files_not_average(geno_test):
	'''Test that genotype file contains x + y identical columns for each strain,
	where x is the number of females in that strain, and y is the number of males
	'''
	@classmethod
	def setUpClass(cls):
		super().buildFiles(cls, False)

	def test_not_average(self):
		correct_output = '''id,,,OB_642,OB_643,OB_644,OB_645,OB_646,OB_647,OB_794,OB_795,OB_847,OB_848,OB_125,OB_126,OB_127,OB_638,OB_639,OB_640,OB_641
rs6196410,1,33.7580975,A,A,A,A,A,A,A,A,A,A,B,B,B,B,B,B,B
rs27034352,11,54.085187,B,B,B,B,B,B,A,A,A,A,A,A,A,A,A,A,A
rs29588301,13,44.7742875,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B
rs29568258,13,45.250384,B,B,B,B,B,B,B,B,B,B,H,H,H,H,H,H,H
rs50906391,16,22.8040365,A,A,A,A,A,A,B,B,B,B,B,B,B,B,B,B,B
rs6262668,3,75.764573,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B
rs32595055,5,17.9862455,A,A,A,A,A,A,B,B,B,B,A,A,A,A,A,A,A
rs31196255,7,57.8978535,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A
rs36773429,9,42.7108535,B,B,B,B,B,B,A,A,A,A,A,A,A,A,A,A,A
rs29270490,X,66.918496,A,A,A,A,A,A,A,A,A,A,B,B,B,B,B,B,B
'''
		super().compareFiles(type(self), correct_output)
