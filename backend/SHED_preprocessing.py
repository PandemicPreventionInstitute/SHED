
def generate_lineage_abundance(PATH, SRA_id):
    '''
    Takes the lineages tsv file and outputs the abundance per lineage in a csv
    '''
    
    with open(PATH + "endpoints/" + SRA_id + ".lineages.tsv") as f:
        for line in f:

            l=line.split('\t')
            lin_dt.append(l)


    lineage = [x.split(' ') for x in lin_dt[2]][1]
    abundance = [x.split(' ') for x in lin_dt[3]][1]
    lin_abun = pd.DataFrame(np.column_stack((lineage, abundance)), columns = ("lineage", "abundance"))
    lin_abun['lineage'] = lin_abun['lineage'].apply(lambda row_str: row_str.strip('\n'))
    lin_abun
                               
    return lin_abun.to_csv(PATH + SRA_id + '_lin_abun.csv', index = False)


def generate_primer_readcnt(PATH, folder_ext, SRA_id):
    '''
    
    Takes a trim log of a SRA and returns the primer name for each read and the count of that read
    '''
    
    infile = PATH + 'trim_logs/' + SRA_id + '.trim.log' ## need to change
    with open(infile) as f:
        f = f.readlines()

    primer_read_cnts = []
    i = 0
    start = 0
    for line in f:

        if start == 1:
            i += 1
            primer_read_cnts.append(line)
        if line == "Results: \n":
            start = start + 1
        if (line == '\n') & (len(primer_read_cnts)>1):
            start = start - 1

    primer_read_list = pd.DataFrame([x.split('\t') for x in primer_read_cnts][1:-1], columns = ("Primer name", "Read count"))
    primer_read_list["Read count"] = primer_read_list["Read count"].apply(lambda row_str: row_str.strip('\n'))
    
    return primer_read_list.to_csv(PATH + SRA_id + '_primer_readcnt.csv', index = False)


def read_cnt_after_filter(PATH, SRA_id):
    '''
    Take SRA id as a string and from the .pe.json or .se.json 
    outputs the number of good quality reads in that sample
    '''
    
    import json
    f = open(PATH+'qc_jsons.zip/' + SRA_id + '.pe.json')
    data = json.load(f)
    
    return data['summary']['after_filtering']['total_reads']

