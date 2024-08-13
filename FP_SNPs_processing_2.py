#########################################################################################################################################
# #
# # Imports
# #
#########################################################################################################################################

import os
import sys
import pandas as pd
import pysam
import logging
from datetime import datetime

##########################################################################################################################################
# #
# # Logging configuraion
# #
##########################################################################################################################################
# # 
# # Log file is created in the directory, where the script works
# # 
logging.basicConfig(
	filename='time.log',  # Log file name
	level=logging.INFO,      # Set the logging level
	format='%(asctime)s - %(message)s',  # Log format with timestamp
)
##########################################################################################################################################
# #
# # Functions_definitions
# #
##########################################################################################################################################
# #
##########################################################################################################################################
# #
# # Logging message call
# # 
##########################################################################################################################################
# #
# #
def log_message(message):
	"""Log a message with a timestamp."""
	logging.info(message)
# #
##########################################################################################################################################
# #
# # Validation step. Error handling. 
# #
##########################################################################################################################################
# #
# #
def validate_tsv_file(tsv_file):
	#
	print("Starting TSV file validation process...")
	#
	log_message("Validation of the TSV file started!")
	#
	# Load the TSV file into a DataFrame
	try:
		df = pd.read_csv(tsv_file, sep='\t')
	except Exception as e:
		print(f"Error reading the TSV file: {e}")
		print("Check as well the proper file format and that it is not damaged")
	#
	log_message("Loading completed! Good!")
	# Define the expected column order
	expected_columns = ['#CHROM', 'POS', "RS_ID", "ALLELE_1", "ALLELE_2"]
	#
	log_message("Checking for missing columns or incorrect columns order...")
	# Checking for missing columns
	missing_columns = [col for col in expected_columns if col not in df.columns]
	if missing_columns:
		print(f"Error: Missing columns in the TSV file, expected: {missing_columns}")
		return False
	#
	# Checking for correct columns order
	if list(df.columns) != expected_columns:
		print("Error: Columns are not in the expected order.")
		return False
	#
	log_message("All columns present, the order is correct, checking the missing values...")
	#
	# Checking for missing values in required columns
	for col in expected_columns:
		if df[col].isnull().any():
			print(f"Error: Missing values found in column '{col}'.")
			return False
	#
	log_message("No missing values, good! Validating the datatypes in POS and RS_ID columns...")
	#
	# Validate data types of RS_ID
	if not pd.api.types.is_string_dtype(df['RS_ID']):
		print("Error: 'RS_ID' must be of string type.")
		return False
	#
	# Validate data types of POS
	if not pd.api.types.is_numeric_dtype(df['POS']):
		print("Error: POS must be numeric.")
		return False
	#
	log_message("Datatypes in POS and RS_ID columns validated! Nice! Checking whether all alleles are correct...")
	#
	# Validate content of alleles
	# Set of correct alleles
	#
	valid_alleles = {'A', 'T', 'C', 'G'}
	#
	# Set of invalid alleles: 
	# Checking whether an allele 1 or allele 2 is present in the set
	# If present in valid => True, else False, if any of them, then False, 
	# if any allele is invalid the row is included in the dataframe, else it is empty
	#
	invalid_alleles = df[~df['ALLELE_1'].isin(valid_alleles) | ~df['ALLELE_2'].isin(valid_alleles)]
	#
	# If not empty, then there will be an error
	#
	if not invalid_alleles.empty:
		print("Error: Invalid alleles found in the TSV file.")
		return False
	#
	# Check for duplicates based on RS_ID
	#
	log_message("Alleles are correct! Checking whether there are duplicates according to the RS_ID...")
	#
	if df['RS_ID'].duplicated().any():
		print("Error: Duplicate RS_IDs found in the TSV file.")
		return False
	#
	log_message("No duplicates found - well done! File is correct! Starting processing!")
	#
	print("TSV file validation passed.")
	return True
# #
##########################################################################################################################################
# #
##########################################################################################################################################
# #
# # Processing using pysam library
# #
##########################################################################################################################################
# #
# #
def is_reference_allele(reference_dir, chromosome, position, provided_allele):
	# Construct the path to the chromosome FASTA file
	reference_fasta = os.path.join(reference_dir, f"GRCh38.d1.vd1_{chromosome}.fa")
	#
	# Check if the file exists
	if not os.path.isfile(reference_fasta):
		raise FileNotFoundError(f"Reference file for {chromosome} not found: {reference_fasta}")
	#
	# Open the reference genome for the specified chromosome
	with pysam.FastaFile(reference_fasta) as fasta:
		# Get the reference base at the specified position (1-based)
		ref_base = fasta.fetch(chromosome, position - 1, position)  # position - 1 for 0-based indexing
	#
	# Compare the provided allele with the reference base
	return provided_allele == ref_base
# #
# #
def check_reference_alleles(tsv_file, reference_dir):
	#
	log_message("Now we start checking reference alleles")
	#
	# Read the .tsv file into a DataFrame
	df = pd.read_csv(tsv_file, sep='\t')
	#
	# Initialize a list to store results
	results = []
	#
	# Process each row in the DataFrame
	for index, row in df.iterrows():
		chromosome = row['#CHROM']
		position = row['POS']
		allele1 = row['ALLELE_1']
		allele2 = row['ALLELE_2']
		#
        # Check which alleles are reference alleles
		is_allele1_ref = is_reference_allele(reference_dir, chromosome, position, allele1)
		is_allele2_ref = is_reference_allele(reference_dir, chromosome, position, allele2)
		#
		if is_allele1_ref == True:
			# Store the results
			results.append({
			'#CHROM': chromosome,
			'POS': position,
			'RS_ID': row['RS_ID'],
			'REF': allele1,
			'ALT': allele2
			})
		#
		elif is_allele2_ref == True:
			# Store the results
			results.append({
			'#CHROM': chromosome,
			'POS': position,
			'RS_ID': row['RS_ID'],
			'REF': allele2,
			'ALT': allele1
			})
	#
	# Convert results to DataFrame for better output handling
	results_df = pd.DataFrame(results)
	#
	log_message("Checking reference alleles finished successfully!")
	#
	return results_df
#
# #
###########################################################################################################################################
# #
# # Main function. Script management.
# #
###########################################################################################################################################
def main():
	print("""Welcome to the FP_SNPs processing script!
			Please provide key:value pairs and continue to processing...

			If you need help, provide -h or --help argument 
			to the python script to display the help message

		You will have to provide at least three mandatory key:value pairs:

		| Reference_fasta_files_dirpath:Reference FASTA Directory path |
		| Input_tsv_filename_fullpath  : Full Path to input TSV file   |
		| Output_tsv_filename_fullpath : Full Path for output TSV file |

		""")
	# Check whether provided argument is help requirement
	if len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
		print("""	
											Mandatory keys:
							| "Reference_fasta_files_dirpath": Directory path             |
							| Input_tsv_filename_fullpath: Full Path to input TSV file    |
							| Output_tsv_filename_fullpath: Full Path for output TSV file |

											Common keys:
										|		-h, --help          |

												Main task:
				This is a Python script to process FP_SNPs_10k_GB38_twoAllelsFormat.tsv file
				The TSV file has following fields: 
				[ chr#, SNP_coordinate_in_dbGAP, RS_ID, allele_1, allele_2 ]
				This script checks the alleles present in TSV file in last two columns 
				and in the output file Results.tsv puts 
				the reference allele in the first column of the output .tsv file
				the alternative allele in the last column of the output .tsv file
			
			""")
		return
	# Check if there are enough arguments
	if len(sys.argv) < 4:
		print("Please provide 'key:value' pairs for mandatory keys.")
		print("Mandatory keys are:")
		print("Reference_fasta_files_dirpath")
		print("Input_tsv_filename_fullpath")
		print("Output_tsv_filename_fullpath")
		return
	# Length of the input string
	elif len(sys.argv) >= 4:
		# Process the key:value pairs
		key_value_dict = {}
		required_keys = ["Reference_fasta_files_dirpath", 
						"Input_tsv_filename_fullpath", 
						"Output_tsv_filename_fullpath"]
		# #
		for pair in sys.argv[1:]:
			if ":" in pair:
				key, value = pair.split(':', 1)
				key_value_dict[key.strip()] = value.strip()
				# #
		for key in required_keys:
			if key not in key_value_dict:
				print(f"Error : Missing mandatory key '{key}'")
				return
		# #
		# # If all mandatory keys are provided, continue with processing
		# #
		print("All mandatory keys are provided! Proceeding with file validation step...")
		# #
		# #
		try:
			reference_dir = key_value_dict["Reference_fasta_files_dirpath"]
			tsv_file = key_value_dict["Input_tsv_filename_fullpath"]
			output_file = key_value_dict["Output_tsv_filename_fullpath"]
			is_valid = validate_tsv_file(tsv_file)
			# #
			if is_valid:
				print("Nicely done! File is correct! Proceeding with processing step...")
				results_df = check_reference_alleles(tsv_file, reference_dir)
				# #
				results_df.to_csv(output_file, sep="\t", index=False)
				print("We have finished! All good! See you!")
			else:
				log_message("Validation failed. Please correct the errors.")
				print("Bad luck! Validation failed. Please correct the errors.")
		except FileNotFoundError as e:
			print(f"Error: {e}")
			# #
	else:
		print(f"Invalid pair: {pair}")
############################################################################################################################################
# #
# # Processing function launch
# #
############################################################################################################################################
if __name__ == '__main__':
	main()
# #
############################################################################################################################################