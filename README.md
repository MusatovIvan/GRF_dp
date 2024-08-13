# GRF_dp

## Introduction

This is a pipeline to process the data (FP_SNPs.txt) received from the GRAF software (version 2.4): 
https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/Software.cgi.
The basic article is as follows: «Quickly identifying identical and closely related subjects in large databases \
using genotype data»: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5469481/

The general task is to define, which of two alleles is a reference or an alternative allele.
The preprocessing script assumes, that the user has a python version not lower than 3.8.10. and all standard built-in libraries installed.
Basically there are two main steps in this task: preprocessing, main processing

### 1. Preprocessing
   Preprocessing provides a file in .TSV format transforming FP_SNPs.txt file into a .TSV file (FP_SNPs_10k_GB38_twoAllelsFormat.tsv)
   with columns '#CHROM', 'POS', 'RS_ID', 'ALLELE_1', 'ALLELE_2':
   1.1. The initial FASTA file was downloaded and unzipped via standard gzip program. \
   Downloaded from: https://gdc.cancer.gov/about-data/data-harmonization-and-generation/gdc-reference-files/GRCh38.d1.vd1.fa.gz \
   1.2 GRAF software was downloaded, unzipped and the FP_SNPs.txt file was extracted to the destination folder. \
   Downloaded from: http://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/GetZip.cgi?zip_name=GRAF_files.zip
   ```sh
   cd download_folder/ 
   gzip -d GRCh38.d1.vd1.fa.gz
   mv ./GRCh38.d1.vd1.fa /destination/folder/
   #   
   tar -xzf destination/folder/file.tar.gz && rm destination/folder/file.tar.gz
   #
   ```
   1.3 The next step assumes that the files were downloaded, unzipped and moved to their destination folder. \
   The python script is used to allow files preprocessing during which: \
     1.3.1 The initial FASTA file will be split into pieces according to the number of the chromosome. \
     1.3.2 Initial FP_SNPs.txt will be transformed into a VCF-like file \
   To preprocess files you will need to launch the preprocessing script and provide two arguments separated by whitespace \
   in a key:value format. The basic keys accepted by script are: --snp, --reference. The keys are not positional. \
   
   Example:
   ```sh
   python3 Preprocessing_script.py --snp Value: /type/your/path/here/FP_SNPs.txt --reference:/type/your/path/here/GRCh38.d1.vd1.fa
   ```
   Once you enter the script the welcome message with instructions will be shown.
   The preprocessed .txt file is transformed into a VCF-like file with extension .tsv

   Note: The initial file FP_SNPs.txt has the following columns: rs#, chromosome, GB37_position, GB38_position, allele_1, allele_2

    The preprocessing script
   1. Removes the GB37_position column and leaves only GB38 position, which is specified as POS in the output file \
   2. Moves the columns in the following order: '#CHROM', 'POS', 'RS_ID', 'ALLELE_1', 'ALLELE_2' \
   3. Appends "chr" string to the number of chromosome: instead "1" we get "chr1" \
   4. Appends "rs" string to the number of RS_ID: instead "4184584" we get "rs4184584" \
      Reference SNP cluster ID - rsID number is a unique label ("rs" followed by a number) used by researchers and databases to identify a specific SNP (Single Nucleotide Polymorphism)) \

   Note: One might do the same preprocessing in bash, if it is preffered. In this pipeline the pythonic way is implemented.

### 2. Main processing

The provided processing Python script can be launched as provided, assuming that 
1. All necessary libraries have been installed (using docker or somehow else) \
2. All mandatory key:value pairs have been provided (see below) \

Probable solution is to install docker on your system and build a docker image,
launching the docker container with all required libraries and dependencies as provided in the pipeline.

To install docker on Linux user might do the following:
```sh
sudo apt update
sudo apt install docker*
```
One might find useful the following post for installation on Linux-Mint or Ubuntu: https://linuxhint.com/install_docker_linux_mint/
If you have Windows, you might get the whole package just downloading docker from the official website.

Once docker is installed you will need to use the provided "Dockerfile", to build the docker image.
```sh
docker build -t snpprocimg .
```
The basic image is built on the basis of Ubuntu.22.04
When docker container is run the python script is launched automatically
user just needs to specify the folder to mount to container, where the required data lay.

One possible way to launch the Python processing script is to run the docker as follows:
```sh
docker run -it -v <path_where_chromosomes_and_tsv_file_lay_mount_to_data>:/data snpprocimg /bin/bash
python3 FP_SNPs_processing_2.py Reference_fasta_files_dirpath:/data/Chromosomes Input_tsv_filename_fullpath:/data/FP_SNPs_10k_GB38_twoAllelsFormat.tsv Output_tsv_filename_fullpath:/data/Results_000.tsv

```
Note: It is expected that the reference chromosomes lay in the Chromosomes folder, whereas the Input_tsv_file lays directly in the folder mounted as a volume to container,
according to this manner, the output will be in the same folder, which is mounted to the docker container. The output here is called Results_000.tsv, but the user can call it otherwise.

The docker image contains 5 bioinformatic libraries with their dependencies: SAMTOOLS, HTSLIB, LIBDEFLATE, VCFTOOLS, BCFTOOLS
All tools are installed in the /soft directory, the processing script specifically is in the /app folder.

To launch any of these tools once the docker image snpprocimg is run, user can type the tool name in capital letter with the ' $ ' sign.

Example:
```sh
docker run -it -v /media/ivan/Transcend/GrafPkg/data/Preproc:/data snpprocimg /bin/bash

cd app/

$SAMTOOLS --version
$HTSLIB --version
$LIBDEFLATEGUNZIP -V
$LIBDEFLATEGZIP -V
$BCFTOOLS --version
$VCFTOOLS --version
```
Note: VCFTOOLS is launched with VCFtools_wrapper.sh, 
the wrapper gets the version of the VCFTOOLS if $VCFTOOLS --version is typed
if any other command is typed vcftools of the indicated version will be launched
This pipeline uses the VCFTOOLS-0.1.16 version.

If user wants to check the system paths of the installed programs, he might type:
```
docker inspect snpprocimg --format='{{json .Config.Env}}'
```
All versions might be found in the environment files which are installed in the /soft directory.

Once launched, processing python script shows a welcome message with instructions.

If the user needs help, typing -h or --help, will give him the desired help message.
The provided .tsv file is validated before being processed for several types of errors:

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

- Definition of the reference and alternative alleles in the .tsv file

For script execution you will have to provide at least three mandatory key:value pairs:

								Mandatory key:value pairs

		| Reference_fasta_files_dirpath:Reference FASTA Directory path |
		| Input_tsv_filename_fullpath  : Full Path to input TSV file   |
		| Output_tsv_filename_fullpath : Full Path for output TSV file |

Main task of the processing script:

Python script processes FP_SNPs_10k_GB38_twoAllelsFormat.tsv file
The TSV file has following fields: 
[ CHROM#, POS, RS_ID, allele_1, allele_2 ]
This script: 
checks the alleles present in TSV file in last two columns 
and in the output file Results.tsv puts 
the reference allele in the first column of the output .tsv file
the alternative allele in the last column of the output .tsv file

The output file has following fields
[ CHROM#, POS, RS_ID, REF, ALT ]

The script also provides a simple log file as time.log, giving timestamps of the script execution
File time.log can be found in /app/ directory with the FP_SNPs_processing_2.py

If you want to see the whole time.log file you can type:
```sh
cat time.log
```
