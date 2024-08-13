# FP_SNPs_README.md

Here we describe the preprocessing in short and more extended we describe processing the data with FP_SNPs_processing_2.py script.

The preprocessed file can be acquired as described in README.md.

In short the user needs to provide a full path to the file FP_SNPs.txt, and to reference genome FASTA file using
key:value pairs --snp Value: /type/your/path/here/FP_SNPs.txt --reference:/type/your/path/here/GRCh38.d1.vd1.fa
Example: 

```python3 Preprocessing_script.py --snp Value: /type/your/path/here/FP_SNPs.txt --reference:/type/your/path/here/GRCh38.d1.vd1.fa```

# The preprocessing script
- Removes the GB37_position column and leaves only GB38 position, which is specified as POS in the output file
- Moves the columns in the following order: '#CHROM', 'POS', 'RS_ID', 'ALLELE_1', 'ALLELE_2'
- Appends "chr" string to the number of chromosome: instead "1" we get "chr1"
- Appends "rs" string to the number of RS_ID: instead "4184584" we get "rs4184584" Reference SNP cluster ID - rsID number is a unique label ("rs" followed by a number) used by researchers and databases to identify a specific SNP (Single Nucleotide Polymorphism))

# Processing python script

1. If the user needs help, typing -h or --help, will give him the desired help message. 

2. The provided .tsv file is validated before being processed for several types of errors:

- Error during reading
- Unexpected column order
- Missing columns
- Correct columns order
- Missing values in required columns
- Wrong data types of RS_ID and POS
- Incorrect nucleotide letters in alleles columns (Invalid alleles)
- Check for duplicates based on RS_ID

If the file has errors inside, then user will have to check it before using the script

Once checked, the file proceeds to processing:

Definition of the reference and alternative alleles in the .tsv file
For script execution you will have to provide at least three mandatory key:value pairs:

		      Mandatory key:value pairs

	| Reference_fasta_files_dirpath :  Reference FASTA_Directory_path |
	| Input_tsv_filename_fullpath   :  Full_Path_to_input_TSV_file    |
	| Output_tsv_filename_fullpath  :  Full_Path_for_output_TSV_file  |
Main task of the processing script:

Python script processes FP_SNPs_10k_GB38_twoAllelsFormat.tsv file The TSV file has following fields: [ CHROM#, POS, RS_ID, allele_1, allele_2 ] This script: checks the alleles present in TSV file in last two columns and in the output file Results.tsv puts the reference allele in the first column of the output .tsv file the alternative allele in the last column of the output .tsv file

The output file has following fields [ CHROM#, POS, RS_ID, REF, ALT ]

The script also provides a simple log file as time.log, giving timestamps of the script execution File time.log can be found in /app/ directory with the processing script itself - the FP_SNPs_processing_2.py

## Script structure
The script has the following structure:
1. Imports
2. Logging configuration
3. Functions_definitions
  3.1 Logging message call
  3.2 Validation step and error handling
4. Processing using pysam library
5. Main function. Script management

Firstly all required libraries are imported, then the logging configuration for a script is perfromed using built-in logging module.
The main() function manages the script work and calls all other functions, when the script is launched.
It prints the welcome and help messages, orders to receive the required mandatory keys and processes the keys, if they are provided correctly. 
If the keys are provided incorrectly, the error message will be returned.
It launches the validate_tsv_file() function, which checks the .tsv file and provides either the error message for each type of error and "FALSE" boolean, 
or, if the file is correct, it returns "TRUE" boolean. Then after condition check if the validate_tsv_file() function returns "TRUE" the check_reference_alleles() function passes through
the pandas dataframe obtained during reading the tsv file, to check for alleles in each row, which of these alleles is a reference allele, according to the provided reference files previously
acquired during preprocessing of the reference GRCh38.d1.vd1.fa, each chromosome will be the special file named accordingly to the chromosome like
GRCh38.d1.vd1_chr1.fa. The pysam library used by is_reference_allele() function automatically indexes the questioned FASTA file, to check quickly the letter on the specified position, 
and the files GRCh38.d1.vd1_chr1.fai are used to check whether the specified nucleotide is a reference or an alternative allele, if the provided allele is same as reference, so 
that during comparison the function returns TRUE, then the allele will be put in the REF column of the output file,
if otherwise, then it will be put in the second column of the output file. 
The output file will get the dataframe returned by check_reference_alleles() function, transformed back to tsv file with df.to_csv() method.

More detailed comments on each important line of the FP_SNPs_processing_2.py code the user might find inside the file itself.

