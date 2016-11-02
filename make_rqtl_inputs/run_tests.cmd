REM thon -m unittest test/test_Individual.py
REM thon -m unittest test/test_Individual_averaged.py
REM thon -m unittest test/test_Strains.py
REM thon -m unittest test/test_Significant_value.py
REM python -m unittest test/test_make_phenotype_files.py
REM python -m unittest test/test_make_genotype_files.py
cls
python -m unittest discover test
