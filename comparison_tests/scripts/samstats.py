#!/bin/env python3

# written by Devon Gregory
# script to pull basic information (total reads mapped / unmapped ) from sam files to compare different mapping programs
# last edited on 3-31-22

import os
import sys

out_fh = open('SAM_stats.txt', 'w')
for file in os.listdir(os.getcwd()):
    if file.lower().endswith('.sam'): # search current directory for sam files to process. 
        filenamesplit = file.split('.')
        print(file)
        sam_file = open(file, 'r')
        count = 0
        mapped = 0
        unmapped = 0
        ntmapped = 0
        for line in sam_file:
            if not line.startswith('@'): # skip header lines, then collect info on whether read was mapped or not.
                count += 1
                split_line = line.split("\t")
                if split_line[2] == '*':
                    unmapped += 1
                else:
                    mapped += 1
                    ntmapped += len(split_line[9])

        sam_file.close()
        out_fh.write(f"{file}\nTotal read lines: {count}\nMapped: {mapped}(nts:{ntmapped})\tUnmapped{unmapped}\n\n")
out_fh.close()
