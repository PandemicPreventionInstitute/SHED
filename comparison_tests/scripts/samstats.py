#!/bin/env python3

# script to pull information from mapped reads in sam files to compare different mapping programs

import os
import sys
sam_info = {} # dict to collect mapping info for each read, not recommended to run this part of the script on all sam, better to limit to 2 or 4.
out_fh = open('SAM_stats.txt', 'w')
for file in os.listdir(os.getcwd()):
    if file.lower().endswith('.sam'): # search current directory for sam files to process.  Add specifics to limit comparison ei 'and file.startswith('SRR15128978'):'
        filenamesplit = file.split('.')
        # inseqs = filenamesplit[0]+filenamesplit[2]
        # prog = filenamesplit[1]
        # try:
            # sam_info[inseqs][prog] = {}
        # except:
            # sam_info[inseqs] = {prog : {}}


        print(file)
        sam_file = open(file, 'r')
        count = 0
        mapped = 0
        unmapped = 0
        ntmapped = 0
        for line in sam_file:
            if not line.startswith('@'): # skip header lines, then collect info on weather read was mapped or not.
                count += 1
                split_line = line.split("\t")
                if split_line[2] == '*':
                    unmapped += 1
                else:
                    mapped += 1
                    ntmapped += len(split_line[9])
                # get specific mapping info for the read split_line[0] is read id, [1] is mapping flag, [3] is genome position, [4] is CIGAR
                # try:
                    # sam_info[inseqs][prog][split_line[0]+'-'+split_line[1]]
                # except:
                    # sam_info[inseqs][prog][split_line[0]+'-'+split_line[1]] = [split_line[3], split_line[5]]
                # else:
                    # sam_info[inseqs][prog][split_line[0]+'-'+split_line[1]] = [split_line[3], split_line[5]]


        sam_file.close()
        out_fh.write(f"{file}\nTotal reads: {count}\nMapped: {mapped}(nts:{ntmapped})\tUnmapped{unmapped}\n\n")
out_fh.close()

# write out reads that were mapped differently into file and collect imperfect stats
# sam_mm_fh = open('sam_mismatches.tsv', 'w')

# for inseqs in sam_info:
    # sam_mm_fh.write(f"{inseqs}\n")
    # mismatches = 0
    # bwaonly = 0
    # mmonly = 0
    # for line in sam_info[inseqs]['bwamem']:
        # if not line in sam_info[inseqs]['mm']: # checks if read was mapped in the sam way (has the same flag)
            # bwaonly +=1
            # sam_mm_fh.write(f"{line}\t{sam_info[inseqs]['bwamem'][line][0]}\t{sam_info[inseqs]['bwamem'][line][1]}\n")
        # elif not sam_info[inseqs]['bwamem'][line][0] == sam_info[inseqs]['mm'][line][0]: # checks to see if reads were mapped to the same position
            # if sam_info[inseqs]['mm'][line][1].split('S')[0].isnumeric(): # account for short soft clipping a the start of the read by minimap2
                # if not int(sam_info[inseqs]['mm'][line][1].split('S')[0]) == (int(sam_info[inseqs]['mm'][line][0]) - int(sam_info[inseqs]['bwamem'][line][0])):
                    # mismatches += 1
                    # sam_mm_fh.write(f"{line}\t{sam_info[inseqs]['bwamem'][line][0]}\t{sam_info[inseqs]['bwamem'][line][1]}\t{sam_info[inseqs]['mm'][line][0]}\t{sam_info[inseqs]['mm'][line][1]}\n")
            # else:
                # mismatches += 1
                # sam_mm_fh.write(f"{line}\t{sam_info[inseqs]['bwamem'][line][0]}\t{sam_info[inseqs]['bwamem'][line][1]}\t{sam_info[inseqs]['mm'][line][0]}\t{sam_info[inseqs]['mm'][line][1]}\n")
    # for line in sam_info[inseqs]['mm']: # compliment to previous flag check
        # if not line in sam_info[inseqs]['bwamem']:
            # mmonly += 1
            # sam_mm_fh.write(f"{line}\t\t\t{sam_info[inseqs]['mm'][line][0]}\t{sam_info[inseqs]['mm'][line][1]}\n")
    # sam_mm_fh.write(f"Diff mapping:{mismatches}\tBWA only:{bwaonly}\tMM only:{mmonly}\n")
    # print(inseqs)
    # print(f"Diff mapping:{mismatches}\tBWA only:{bwaonly}\tMM only:{mmonly}\n") # imperfect reporting
    # sam_mm_fh.write("\n")

# sam_mm_fh.close()