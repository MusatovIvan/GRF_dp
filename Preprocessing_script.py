#################################################################################################################################
# #
# # Imports
# #
#################################################################################################################################
import os
##################################################################################################################################
# #
# # Functions_definitions
# #
##################################################################################################################################
# #
# # Preprocessing
# #
##################################################################################################################################
# #
# # Transforming FP_SNPs.txt into a VCF-like file
# # 
# # Downloaded from: http://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/GetZip.cgi?zip_name=GRAF_files.zip
# # 
# # The file was taken from the provided package (weblink above) of the GRAF_2.4 program
# #
##################################################################################################################################
def file_preprocessing_to_VCF_like(input_FP_SNP_txt_filename_fullpath):
	"""
	Transforms the program GRAF 2.4 custom file into VCF-like file

	Parameters: 

	-input_fp_snp_txt_path: full path to the FP_SNP txt file 

	"""
	dirname = os.path.dirname(input_FP_SNP_txt_filename_fullpath)
	input_filename = os.path.basename(input_FP_SNP_txt_filename_fullpath)
	output_filename = "FP_SNPs_10k_GB38_twoAllelsFormat.tsv"
	output_filename_fullpath = os.path.join(dirname, output_filename)
	with open(output_filename_fullpath, "wt") as output_file:
		with open(input_FP_SNP_txt_filename_fullpath, "rt") as input_file:
			header = input_file.readline()
			preprocessed_results = []
			new_header = "#CHROM\tPOS\tRS_ID\tALLELE1\tALLELE2"
			preprocessed_results.append(new_header)
			line_index = 0
			print(new_header, file=output_file)
			for line in input_file:
				line = line.strip().split()
				chr_n = 'chr' + line[1]
				output_line = ""
				line_index += 1
				if len(line) < 6:
					print(f"The line number '{line_index} is missing columns'.")
					continue

				if chr_n != "chr23":
					rs_id = 'rs'+ line[0]
					hg_38_pos = line[3]
					allele_1 = line[4]
					allele_2 = line[5]
					
					# Create a tab-separated string
					output_line = '\t'.join([chr_n, hg_38_pos, rs_id, allele_1, allele_2])
					preprocessed_results.append(output_line)
					print(output_line, file=output_file)
############################################################################################################################################
# #
# # Splitting the Reference genome file GRCh38.d1.vd1.fa into separate chromosomes
# #
# # Downloaded from: https://gdc.cancer.gov/about-data/data-harmonization-and-generation/gdc-reference-files/GRCh38.d1.vd1.fa.gz
# #
############################################################################################################################################
def REF_hg38_FASTA_to_small_files_split(input_reference_genome_file):
	"""
	Splits a FASTA file into separate files for each chromosome

	Parameters:
	- input_fasta_path: full path to the input FASTA file

	"""
	dirname = os.path.dirname(input_reference_genome_file)

	try:
		with open(input_reference_genome_file, "rt") as input_file:
			output_file = None

			for line in input_file:
				line = line.strip()  # Strip whitespaces

				# Check if the line is a chromosome header
				if line.startswith(">chr"):
					# Close the previous output file if it's open
					if output_file:
						output_file.close()

					# Create a new filename for the current chromosome
					chr_n = line.strip(">chr").split()[0]
					new_FASTA_filename = f"GRCh38.d1.vd1_chr_{chr_n}.fa"
					new_FASTA_filename_fullpath = os.path.join(dirname, new_FASTA_filename)

					# Open a new output file for writing
					output_file = open(new_FASTA_filename_fullpath, "wt")
					output_file.write(line + "\n")  # Write the header line

				else:
					# If we are currently writing to an output file, write the sequence line
					if output_file:
						output_file.write(line + "\n")

			# Close the last output file if it was opened
			if output_file:
				output_file.close()
	except Exception as e:
		print(f"Error occured in the script: {e}")
# #
##############################################################################################################################################
# #
# # Main function. Script management.
# #
##############################################################################################################################################
# #
def main():
	print("Welcome to the preprocessing script!")
	print("""Please provide two arguments separated by a space:
		1. --snp: Fullpath to GRAF txt_file (e.g. FP_SNPs.txt);
		2. --reference: Fullpath to GRCh38.d1.vd1 fasta_file of reference_genome.
		Examples:
		--snp:/path/to/FP_SNP.txt --reference:/path/to/GRCh38.d1.vd1.fasta
		""")

	# Wait for user input
	user_input = input("Enter your arguments: ")

	# Split the input into a list
	args = user_input.split()

	# Initialize a dictionary to hold the arguments
	arg_dict = {}

	# Parse the key-value pairs
	for arg in args:
		if ':' in arg:
			key, value = arg.split(':', 1)  # Split on the first colon
			arg_dict[key.strip()] = value.strip()
		else:
			print(f"Error: Invalid argument format '{arg}'. Use key:value format.")
			return

	# Check if required keys are present
	if '--snp' not in arg_dict or '--reference' not in arg_dict:
		print("""Error: You must provide both arguments:
			1. --snp: Fullpath to GRAF txt_file;
			2. --reference: Fullpath to GRCh38.d1.vd1 fasta_file of reference_genome.
			Examples:
			--snp:/path/to/FP_SNPs.txt --reference:/path/to/GRCh38.d1.vd1.fasta""")
		return

	# Retrieve the file paths from the dictionary
	input_FP_SNP_txt_filename_fullpath = arg_dict['--snp']
	input_reference_genome_fasta_filename_fullpath = arg_dict['--reference']
	# #
	file_preprocessing_to_VCF_like(input_FP_SNP_txt_filename_fullpath)
	# #
	REF_hg38_FASTA_to_small_files_split(input_reference_genome_fasta_filename_fullpath)
	# #
# #
####################################################################################################################################
# #
# # Preprocessing functions launch
# #
####################################################################################################################################
# #
if __name__ == '__main__':
	main()
# #
####################################################################################################################################