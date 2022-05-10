#! /bin/bash

# written by Devon Gregory
# test for sra_fetch.py
# will download small fastq files from 5 SRA samples based on TestSraList.txt
# last editted on 5-9-22

mkdir fastqs
echo 'starting sra_fetch.py test'
# remove fastq files if they already exist so they won't trigger a pass
rm ./fastqs/ERR5019844*.fastq.gz
rm ./fastqs/SRR15294802*.fastq.gz
rm ./fastqs/SRR17888010*.fastq.gz
rm ./fastqs/SRR15240439*.fastq.gz
rm ./fastqs/SRR17887900*.fastq.gz

# may need to update path
python3 ../modules/sra_fetch.py -i TestSraList.txt
test=1
# make sure all the files were downloaded
if [[ ! -f ./fastqs/ERR5019844.fastq.gz ]]
	then
	echo test failed, ERR5019844.fastq.gz not present
	test=0
fi
if [[ ! -f ./fastqs/SRR15294802_1.fastq.gz ]]
	then
	echo test failed, SRR15294802_1.fastq.gz not present
	test=0
fi
if [[ ! -f ./fastqs/SRR17888010_1.fastq.gz ]]
	then
	echo test failed, SRR17888010_1.fastq.gz not present
	test=0
fi
if [[ ! -f ./fastqs/SRR15240439_1.fastq.gz ]]
	then
	echo test failed, SRR15240439_1.fastq.gz not present
	test=0
fi
if [[ ! -f ./fastqs/SRR17887900_1.fastq.gz ]]
	then
	echo test failed, SRR17887900_1.fastq.gz not present
	test=0
fi
if [[ ! -f ./fastqs/SRR15294802_2.fastq.gz ]]
	then
	echo test failed, SRR15294802_2.fastq.gz not present
	test=0
fi
if [[ ! -f ./fastqs/SRR17888010_2.fastq.gz ]]
	then
	echo test failed, SRR17888010_2.fastq.gz not present
	test=0
fi
if [[ ! -f ./fastqs/SRR15240439_2.fastq.gz ]]
	then
	echo test failed, SRR15240439_2.fastq.gz not present
	test=0
fi
if [[ ! -f ./fastqs/SRR17887900_2.fastq.gz ]]
	then
	echo test failed, SRR17887900_2.fastq.gz not present
	test=0
fi

if test $test -eq 1
	then
	echo "test passed, all fastqs downloaded"
fi

# clean up
rm ./fastqs/ERR5019844*.fastq.gz
rm ./fastqs/SRR15294802*.fastq.gz
rm ./fastqs/SRR17888010*.fastq.gz
rm ./fastqs/SRR15240439*.fastq.gz
rm ./fastqs/SRR17887900*.fastq.gz
