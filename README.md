This program runs a web-based application that takes a mitochondrial haplogroup from user input and outputs a family tree-style graph of the user's decent as well as human-interest information about their evolutionary history based on the work of Soares et al and the Allen Ancient DNA Resource. 

***BEFORE YOU BEGIN***

A yaml file to create a conda environtment in which to run this program is included in the Environments folder. 

To create the conda environment:

>conda env create -n haplogroupStoryteller --file Environments/environment.yml
>
>conda activate haplogroupStoryteller

Note: replace 'Environments/environment.yml' with the appropriate path to the environment.yml file from your working directory

Users will additionally need to download the metadata file 'v62.0_1240k_public.xlsx' from the Allen Ancient DNA Resource, which can be found here: https://dataverse.harvard.edu/file.xhtml?fileId=10537416&version=9.1

A small sample metadata file has been included in this repository. It can be used in place of the v62.0_1240k_public file for testing purposes, but for general use, the program relies on the AADR information. 


***RUNNING THE PROGRAM***

This program is designed to run from the command line according to the following command:

>python haplogroupStoryteller.py AADR_54.1/v62.0_1240k_public.xlsx --lineage_dates lineageDates.txt[optional] --ancient_samples ancientSamples.txt[optional] --modern_samples modernSamples.txt[optional]

if optional arguments are not provided, the program will default to reading the files provided in the Assets folder, which it presumes is located in the same folder as haplogroupStoryteller.py. 

Important: if the Assets folder is moved to a different directory from the haplogroupStoryteller.py program, the user *must* specify the location of all optional files when calling the script.

If the user wishes to use different sources for lineage divergence dates or to add additional ancient or modern DNA ids, they can use the provided files as a formatting template. 


***IN THIS REPOSITORY***

* README.md - this file, contains essential user information

* haplogroupStoryteller.py - the program file

* Assets/ - a folder containing necessary files to run the program
    -Ancient_samples.txt - a list of genetic IDs for the ancient DNA samples in the AADR metadata file
    -Modern_samples.txt - a list of the genetic IDs for the modern DNA samples in the AADR metadata file
    -lineageDates.txt - a list of estimated divergence dates for mtHaplogroup lineages, from Soares et al
    -testData.xlsx - an excel file containing sample information for testing the script 

* Environments/ - a folder containing information for creating a conda environment to run this script
    -environment.yml - the environment parameter file


***QA AND TESTING***

In order to test the functionality of this program, run the following command (with file paths substituted as appropriate):

python haplogroupStoryteller.py Assets/testData.xlsx

when the web interface is open, input either 'U5b2c' or 'X2c2' for proper functionality demonstration. 

***Acknowlegements***

AADR metadata file:

Mallick, Swapan; Reich, David, 2023, "The Allen Ancient DNA Resource (AADR): A curated compendium of ancient human genomes", https://doi.org/10.7910/DVN/FFIDCW, Harvard Dataverse, V9; v62.0_1240k_public.xlsx 

Mitochondrial clock lineage estimates:

Soares, P., Ermini, L., Thomson, N., Mormina, M., Rito, T., Röhl, A., Salas, A., Oppenheimer, S., Macaulay, V., & Richards, M. B. (2009). Correcting for purifying selection: an improved human mitochondrial molecular clock. American journal of human genetics, 84(6), 740–759. https://doi.org/10.1016/j.ajhg.2009.05.001

The author would also like to thank Eran Elhaik, Chandrashekar Chandramouleswara Rajshekar, and Mainak Chakraborty for their support in creating this program. 
