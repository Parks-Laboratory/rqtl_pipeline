from src.makeRQTLInputs import *
import unittest
'''
TODO:
	-Make simple phenotypes.csv for classes in this file to read in
		-Entries should be designed so it can be determined if
		output files are correct
'''

class test_make_phenotype_files_average(unittest.TestCase):
	'''
	Test goals:
		-Need to make sure that output file averages were derived from
		the correct group (Strain then Sex) in input file
		-Don't need to test rounding or scientific notation
		b/c other test classes exist to check for that
	TODO:
		-call make_phenotype_files(simple input file)
		-Open() both generated file and and manually created output file
		-use File.readlines() to get next string of each file
		and assert that they are equal
	'''
	def test(self):
		# TODO decide what test should do


class test_make_phenotype_files_not_averaged(unittest.TestCase):
	def test(self):
		# TODO decide what test should do
		self.assertTrue(True)
