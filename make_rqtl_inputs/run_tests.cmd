REM python -m unittest test/test_Individual_averaged.py
REM python -m unittest test/test_Individual
REM python -m unittest test/test_Strains
REM python -m unittest test/test_Significant_value.py
REM python -m unittest test/test_make_phenotype_files.py
REM python -m unittest test/test_make_genotype_files.py
cls
python -m unittest discover test
