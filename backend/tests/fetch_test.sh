#! /bin/bash

# written by Devon Gregory
# test for sra_fetch.py
# will download small fastq files from 5 SRA samples based on TestSraRunTable.csv
# last editted on 4-5-22

mkdir fastqs
echo 'starting sra_fetch.py test'
# remove fastq files if they already exist so they won't trigger a pass
rm ./fastqs/ERR5019844*.fastq
rm ./fastqs/SRR15294802*.fastq
rm ./fastqs/SRR17888010*.fastq
rm ./fastqs/SRR15240439*.fastq
rm ./fastqs/SRR17887900*.fastq

# may need to update path
python ../modules/sra_fetch.py -i TestSraList.txt
test=1
# make sure all the files were downloaded
if [[ ! -f ./fastqs/ERR5019844_1.fastq ]]
	then
	echo test failed, ERR5019844_1.fastq not present
	test=0
fi
if [[ ! -f ./fastqs/SRR15294802_1.fastq ]]
	then
	echo test failed, SRR15294802_1.fastq not present
	test=0
fi
if [[ ! -f ./fastqs/SRR17888010_1.fastq ]]
	then
	echo test failed, SRR17888010_1.fastq not present
	test=0
fi
if [[ ! -f ./fastqs/SRR15240439_1.fastq ]]
	then
	echo test failed, SRR15240439_1.fastq not present
	test=0
fi
if [[ ! -f ./fastqs/SRR17887900_1.fastq ]]
	then
	echo test failed, SRR17887900_1.fastq not present
	test=0
fi
if [[ ! -f ./fastqs/SRR15294802_2.fastq ]]
	then
	echo test failed, SRR15294802_2.fastq not present
	test=0
fi
if [[ ! -f ./fastqs/SRR17888010_2.fastq ]]
	then
	echo test failed, SRR17888010_2.fastq not present
	test=0
fi
if [[ ! -f ./fastqs/SRR15240439_2.fastq ]]
	then
	echo test failed, SRR15240439_2.fastq not present
	test=0
fi
if [[ ! -f ./fastqs/SRR17887900_2.fastq ]]
	then
	echo test failed, SRR17887900_2.fastq not present
	test=0
fi

if [test == 1]
	then
	echo test passed, all fastqs downloaded
fi

rm ./fastqs/*
rmdir fastqs