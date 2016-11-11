## Synopsis
This README is intended to aid in future modifications to make_rqtl_inputs.py

## Data structure where data not averaged by strain
						Strains (class)					
						/
			strains (dictionary)
		strain (string) --> Individual
                                |
							rows (list) 				(row upon row of phenotype data)
		
		
## Data structure where data averaged by strain
						Strains (class)			
						/
			strains (dictionary)
		strain (string) --> sexes (list)
							/          \
			   females (list)           males (list)	(same as for females)
              /      |     \          
Individual_averaged  ...   ...
        |
	rows (list) 										(row upon row of phenotype data)
