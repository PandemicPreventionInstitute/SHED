#!/bin/env python3

# written by Devon Gregory
# script to pull and print to file detailed information (flag, map position and CIGAR) from read mapping in sam files to compare different mapping programs
# last edited on 3-31-22

import os
import sys

sam_info = {} # dict to collect mapping info for each read, not recommended to run this part of the script on all sam, better to limit to 2 or 4.

for file in os.listdir(os.getcwd()):
     # search current directory for sam files to process.  Add specifics to limit comparison ei 'and file.startswith('SRR15128978'):'
    if file.lower().endswith('.sam'):
        filenamesplit = file.split('.')
        inseqs = filenamesplit[0]+'.'+filenamesplit[2]
        prog = filenamesplit[1]
        try:
            sam_info[inseqs][prog] = {}
        except:
            sam_info[inseqs] = {prog : {}}


        print(file)
        sam_file = open(file, 'r')
        line_count = 0
        for line in sam_file:
            if not line.startswith('@'): # skip header lines, then collect info on read mapping.
                line_count += 1
                split_line =  line.split('\t')
                if not split_line[2] == '*':
                    # get specific mapping info for the read split_line[0] is read id, [1] is mapping flag, [2] is target, [3] is genome position, [4] is CIGAR
                    try:
                        sam_info[inseqs][prog][split_line[0]].append([split_line[1], split_line[3], split_line[5]])
                    except:
                        sam_info[inseqs][prog][split_line[0]] = [[split_line[1], split_line[3], split_line[5]]]
        sam_file.close()
        print(f"{line_count} read lines in {file}")


# write out reads that were mapped differently into file and collect stats

for inseqs in sam_info:
    mismatches = 0
    bwaonly = 0
    mmonly = 0
    softclipmatch = 0
    sam_mism_fh = open(inseqs+'.sam_mismatches.tsv', 'w') # open as new write (overwrites)
    for read_id in sam_info[inseqs]['bwamem']:
        if not read_id in sam_info[inseqs]['mm']: # checks if read was also mapped by minimap2
            bwaonly +=1
            for info in sam_info[inseqs]['bwamem'][read_id]:
                sam_mism_fh.write(f"{read_id}\tbwa only\t{info[0]}\t{info[1]}\t{info[2]}\n")
        else:
            bwa = []
            mm = []
            matched_map = []
            for mapinfo in sam_info[inseqs]['bwamem'][read_id]:
                matched = 0
                # checks for perfect match
                if mapinfo in sam_info[inseqs]['mm'][read_id]:
                    matched = 1
                    matched_map.append(mapinfo)
                else:
                    for mmmapinfo in sam_info[inseqs]['mm'][read_id]:
                        # check for differently flagged perfect match
                        if mapinfo[1:3] == mmmapinfo[1:3]:
                            matched = 1
                            matched_map.append(mmmapinfo)
                        # checks for differnt mapping due to 3' softclipping
                        elif mapinfo[1] == mmmapinfo[1] and (mapinfo[2].endswith('S') or mmmapinfo[2].endswith('S')):
                            matched = 1
                            matched_map.append(mmmapinfo)
                            softclipmatch +=1
                        else: # checks for different mapping due to 5' softclipping
                            bwa_clip = 0
                            mm_clip = 0
                            try:
                                bwa_clip = int(mapinfo[2].split('S')[0])
                            except:
                                pass
                            try:
                                mm_clip = int(mmmapinfo[2].split('S')[0])
                            except:
                                pass
                            if (int(mapinfo[1]) - bwa_clip) == (int(mmmapinfo[1]) - mm_clip):
                                matched = 1
                                matched_map.append(mmmapinfo)
                                softclipmatch +=1
                        
                if matched == 0:
                    bwa.append(mapinfo)
            for mmmapinfo in sam_info[inseqs]['mm'][read_id]:
                if not mmmapinfo in matched_map:
                    mm.append(mmmapinfo)
            # prints out mismatches
            if mm or bwa:
                mismatches += 1
                for i in range(0, max(len(mm), len(bwa))):
                    sam_mism_fh.write(f"{read_id}\tmismatch")
                    try:
                        sam_mism_fh.write(f"\t{bwa[i][0]}\t{bwa[i][1]}\t{bwa[i][2]}")
                    except:
                        sam_mism_fh.write("\t\t\t")
                    try:
                        sam_mism_fh.write(f"\t{mm[i][0]}\t{mm[i][1]}\t{mm[i][2]}")
                    except:
                        sam_mism_fh.write("\t\t\t")
                    sam_mism_fh.write("\n")

    for read_id in sam_info[inseqs]['mm']: # checks for reads only mapped by minimap2
        if not read_id in sam_info[inseqs]['mm']:
            mmonly += 1
            for info in sam_info[inseqs]['mm'][read_id]:
                sam_mism_fh.write(f"{read_id}\t\t\tbwa only\t{info[0]}\t{info[1]}\t{info[2]}\n")

    sam_mism_fh.write(f"Diff mapping:{mismatches}\tsoftclip match: {softclipmatch}\tBWA only:{bwaonly}\tMM only:{mmonly}\n")
    print(inseqs)
    print(f"Diff mapping:{mismatches}\tsoftclip match: {softclipmatch}\tBWA only:{bwaonly}\tMM only:{mmonly}\n") # imperfect reporting
    sam_mism_fh.write("\n")
    sam_mism_fh.close()
