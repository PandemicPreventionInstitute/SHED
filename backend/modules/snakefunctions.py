"""
Writen by Devon Gregory
This script has functions called by the snakefiles to query NCBI'
SRA and download and process the files for the results.
Last edited on 7-10-22
"""

import os
import sys
import subprocess
import xml.parsers.expat
import json
import shutil

snakemodpath = os.path.realpath(os.path.join(sys.path[0], ".."))


def sra_query(search_str: str, date_stamp: str) -> int:
    """
    Called to query NCBI's SRA and collect metadata for the query results.

    Parameters:
    search_str - string for the query - str
    date_stamp - timestamp of current query - str

    Functionality:
        curl is used to download the html results for the query.
        The html is then parsed to find the MCID and key of the specific
        query for downloading the metadata, also using using curl.  Files
        are tagged with the date stamp.

        Searches returning no results (and maybe only 1 result) will cause
        a program exit.

        Return: 0 if no exceptions were raised
    """

    subprocess.run(
        [
            "curl -A 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) "
            "Gecko/20100101 Firefox/50.0' -L --alt-svc '' "
            "--anyauth -b ncbi "
            f"'https://www.ncbi.nlm.nih.gov/sra/?term={search_str}' "
            f"-o search_results_{date_stamp}.html"
        ],
        shell=True,
        check=True,
    )
    mcid = ""
    key = -1
    try:
        with open(
            f"search_results_{date_stamp}.html", "r", encoding="utf-8"
        ) as search_fh:
            mcid = search_fh.read().split('value="MCID_')[1].split('"')[0]
            search_fh.seek(0)
            key = search_fh.read().split("query_key:&quot;")[1].split("&quot")[0]
    except IndexError as err:
        print("Query results can't be used to download metadata")
        print(err)
        sys.exit(2)
    subprocess.run(
        [
            "curl 'https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/sra-db-be."
            f"cgi?rettype=runinfo&WebEnv=MCID_{mcid}&query_key={key}' "
            f"-L -o sra_data_{date_stamp}.csv"
        ],
        shell=True,
        check=True,
    )
    subprocess.run(
        [
            "curl 'https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/sra-db-be."
            f"cgi?rettype=exp&WebEnv=MCID_{mcid}&query_key={key}' "
            f"-L -o sra_meta_{date_stamp}.xml"
        ],
        shell=True,
        check=True,
    )
    return 0


def get_primer_bed(primers_str: str, mapping_file: str) -> str:
    """
    Called to determine  either the proper primer bed or primers used
    based on the str passed.

    NOTE: This function only matches the first key in the dict. Later keys
    that match will be ignored.  json fiels must be formatted in the correct
    order to facilitate proper matching

    Parameters:
    primers_str - string of potential primer info - str
    mapping_file - json file that contains the matching information - str

    Functionality:
        parses the passed string for specific keywords to determine the most
        likely primers used in the sequencing or the primer bed for the found
        potential primers

    Returns string of the bed file or a primer keyword
    """

    with open(
        os.path.join(snakemodpath, mapping_file), "r", encoding="utf-8"
    ) as _primer_map_json:
        _primer_map_dict = json.load(_primer_map_json)
    bed = "Unknown"
    matching_dict = _primer_map_dict
    while isinstance(matching_dict, dict) and bed == "Unknown":
        new_dict = 0
        for key in matching_dict:
            if key in primers_str:
                # Multiple keys may be present in primers_str. Match the first
                # key only.
                if isinstance(matching_dict[key], str):
                    bed = matching_dict[key]
                    break
                matching_dict = matching_dict[key]
                new_dict = 1
                break
            try:
                bed = matching_dict["Other"]
                break
            except KeyError:
                pass
        if new_dict == 0:
            break

    return bed


def start_ele_fun(name, attrs, element_strs, elements_dict, out_fh):
    """
    Called to perform the actions and logic of dealing with the start
    of an xml element.

    Parameters:
    name - name of the element - str
    attrs - dict of elements attributes - dict
    element_strs - list of the elements/subelements - list
    elements_dict - dict to collect metadata from elements - dict
    out_fh - file to write out all metadata - file object

    Functionality:
        parses the passed element info and updates/writes out metadata

    Returns elements_dict
    """

    if len(element_strs) > 1:
        if len(element_strs) > 2:
            for _ in element_strs[2:]:
                out_fh.write("    ")
        out_fh.write(name)
        out_fh.write(" :")
        if attrs:
            out_fh.write(" ")
            out_fh.write(str(attrs))
        out_fh.write("\n")
    if name == "RUN":
        try:
            elements_dict["accession"] = attrs["accession"]
        except KeyError as err:
            elements_dict["accession"] = err

    return elements_dict


def end_ele_fun(element_strs, elements_dict, out_fh, lite_out_fh):
    """
    Called to perform the actions and logic of dealing with the end
    of an xml element.

    Parameters:
    element_strs - list of the elements/subelements - list
    elements_dict - dict to collect metadata from elements - dict
    out_fh - file to write out all metadata - file object
    lite_out_fh - file to write out select metadata - file object

    Functionality:
        parses the passed element info and updates/writes out metadata
        if the sample data has ended

    Returns elements_dict
    """

    if element_strs and len(element_strs) < 2:
        out_fh.write("\n")
        lite_out_fh.write(
            f"{elements_dict['accession']}\t{elements_dict['date']}\t{elements_dict['loc']}\t"
        )
        if elements_dict["primers"]:
            lite_out_fh.write(
                get_primer_bed(
                    "".join(elements_dict["primers"]),
                    "data/primer_mapping.json",
                )
            )
        else:
            lite_out_fh.write("Unknown")
        lite_out_fh.write("\n")
        elements_dict["accession"] = ""
        elements_dict["date"] = ""
        elements_dict["loc"] = ""
        elements_dict["primers"] = []

    return elements_dict


def modify_loc_flag(flags, element_strs, elements_dict, data):
    """
    This function gets/ stores location data and sets the flag for
    getting the data when the xml data for location is
    being parsed

    Parameters:
    flags - dictionary of flags - dict
    element_strs - string for the xml element - str
    elements_dict - dict for data from the xml elements - dict
    data - str of the xml element's data - str

    Functionality:
        Checks to see if the location flag is True and if so stores
        the data for the location and sets the flag back to False.
        Otherwise checks to see if the element is for the location tag
        and sets the flag as True if so.

    Returns loc_flag
    """

    loc_flag = flags["loc"]

    if flags["loc"]:

        if flags["loc"] and element_strs[-1] == "VALUE":
            if elements_dict["loc"]:
                elements_dict["loc"] += ", " + data
            else:
                elements_dict["loc"] = data
        loc_flag = False

    if element_strs[-1] == "TAG" and (
        data == "geo_loc_name"
        or data == "geo loc name"
        or "geographic location" in data
    ):
        loc_flag = True

    return loc_flag


def modify_date_flag(flags, element_strs, elements_dict, data):
    """
    This function gets/ stores collection date and sets the flag for
    getting the data when the xml data for the date is
    being parsed

    Parameters:
    flags - dictionary of flags - dict
    element_strs - string for the xml element - str
    elements_dict - dict for data from the xml elements - dict
    data - str of the xml element's data - str

    Functionality:
        Checks to see if the date flag is True and if so stores
        the data for the collection date and sets the flag back to False.
        Otherwise checks to see if the element is for the date tag
        and sets the flag as True if so.

    Returns loc_flag
    """

    date_flag = flags["date"]

    if flags["date"]:
        if element_strs[-1] == "VALUE":
            elements_dict["date"] = data
        date_flag = False
    if element_strs[-1] == "TAG" and (data in ("collection_date", "collection date")):
        date_flag = True

    return date_flag


def data_fun(data, element_strs, elements_dict, flags, out_fh):
    """
    Called to perform the actions and logic of dealing with the data
    of an xml element.

    Parameters:
    name - name of the element - str
    element_strs - list of the elements/subelements - list
    elements_dict - dict to collect metadata from elements - dict
    flags - dict of flags for collecting specific metadata - dict
    out_fh - file to write out all metadata - file object

    Functionality:
        parses the passed data info and updates/writes out metadata

    Returns elements_dict
    """

    # Add whitespace and newlines to outfile
    if len(element_strs) > 1:
        for _ in element_strs[1:]:
            out_fh.write("    ")
    out_fh.write(data)
    out_fh.write("\n")

    # Modify location and date flags if needed
    flags["loc"] = modify_loc_flag(flags, element_strs, elements_dict, data)
    flags["date"] = modify_date_flag(flags, element_strs, elements_dict, data)

    # Add new primers observed in the data
    new_elements = get_primer_bed(data.upper(), "data/elements_mapping.json")
    elements_dict["primers"].append(new_elements)

    return elements_dict


def parse_xml_meta(date_stamp: str) -> int:
    """
    Called to process the metadata xml for the current query and produce a
    human readable txt file and collect specific sample information into a tsv.

    Parameters:
    date_stamp - timestamp of current query - str

    Functionality:
        The xml file is parsed and translated into a txt file with a (more)
        human readable format (similiar to json).  Sample data on the run accession,
        collection date, geographic location and the sequencing primers used are
        collecting into a tsv.

    Returns 0 if no exceptions were raised
    """

    with open(f"sra_meta_{date_stamp}.xml", "r", encoding="utf-8") as full_meta_in_fh:
        with open(f"sra_meta_{date_stamp}.txt", "w", encoding="utf-8") as out_fh:
            with open(
                f"sra_meta_collect_{date_stamp}.tsv", "w", encoding="utf-8"
            ) as lite_out_fh:
                lite_out_fh.write("Accession\tcollectiong data\tgeo_loc\tprimers\n")
                parse_xml = xml.parsers.expat.ParserCreate()
                element_strs = []
                elements_dict = {
                    "accession": "",
                    "date": "",
                    "loc": "",
                    "primers": [],
                }
                flags = {"date": False, "loc": False}
                # 3 handler functions
                def start_element(name, attrs):
                    element_strs.append(name)
                    start_ele_fun(name, attrs, element_strs, elements_dict, out_fh)

                def end_element(name):
                    # name is used by parse_xml and must be a parameter of this function
                    assert name
                    element_strs.pop()
                    end_ele_fun(element_strs, elements_dict, out_fh, lite_out_fh)

                def char_data(data):
                    if data and data.strip():
                        data_fun(data, element_strs, elements_dict, flags, out_fh)

                parse_xml.StartElementHandler = start_element
                parse_xml.EndElementHandler = end_element
                parse_xml.CharacterDataHandler = char_data
                parse_xml.Parse(full_meta_in_fh.read())
    shutil.copyfile(
        f"sra_meta_collect_{date_stamp}.tsv",
        "sra_meta_collect_current.tsv",
    )
    return 0


def get_sample_acc1(redo: bool) -> list:
    """
    Called to get the accessions of the samples of the current query.

    Parameters:
    bool - boolean for reprocessing samples - bool

    Functionality:
        If reprocessing is not to be done, accessions of previously
        downloaded and processed samples are collected from the current
        meta collected values tsv. Sample accession are check against
        previously processed samples, if relevent, and returned

    Returns a list of the accessions
    """
    prev_accs = []
    if (not redo) and os.path.isdir("fastqs/"):
        for file in os.listdir("fastqs/"):
            if file.endswith(".json"):
                prev_accs.append(file.split(".")[0])
    accs = []
    with open("sra_meta_collect_current.tsv", "r", encoding="utf-8") as in_fh:
        for line in in_fh:
            split_line = line.strip("\n").split("\t")
            if (
                split_line[0]
                and (split_line[0].startswith("SRR") or split_line[0].startswith("ERR"))
                and not split_line[0] in prev_accs
            ):
                accs.append(split_line[0])
    return " ".join(accs)


def get_sample_acc2(redo: bool) -> dict:
    """
    Called to get the accessions of the samples of the current query.

    Parameters:
    bool - boolean for reprocessing samples - bool

    Functionality:
        If reprocessing is not to be done, accessions of previously
        downloaded and processed samples are collected based on the
        presence of the qc json for the sample.
        Sample accession from the current query are check against previously
        processed samples, if relevent, and passed back as a dict with
        primer trimming instructions to be used in rules.

    Returns a dict of the accessions with primer trimming instructions.
    """
    prev_accs = []
    if (not redo) and os.path.isdir("fastqs/"):
        for file in os.listdir("fastqs/"):
            if file.endswith(".json"):
                prev_accs.append(file.split(".")[0])
    accs = {}
    with open("sra_meta_collect_current.tsv", "r", encoding="utf-8") as in_fh:
        for line in in_fh:
            split_line = line.strip("\n").split("\t")
            if (
                split_line[0]
                and (split_line[0].startswith("SRR") or split_line[0].startswith("ERR"))
                and not split_line[0] in prev_accs
            ):
                if os.path.isfile(f"SRAs/{split_line[0]}/{split_line[0]}.sra"):
                    accs[split_line[0]] = {"bed": split_line[3], "cut": ""}
                    if split_line[3] == "Unknown":
                        accs[split_line[0]]["cut"] = "-f 25 "
    return accs


def qc_pass(sample_accs: dict) -> list:
    """
    Called to discover qc checked fastq files generated by the quality_check rule
    and determine if they are of a quality worth continuing.
    Potentilal TODO: have the cut off in the config.yaml and pass it here

    Parameters:
    sample_accs - accession list for the SRA samples - list

    Functionality:
        Checks the fastqs subfolder for single or paired qced fastq files,
        then checks the qc json for sufficient passed reads to conintue.
        Currently requires over 500 passed reads. returns list of passed samples

    Returns list of passed accs
    """

    passed = []
    for acc in sample_accs:
        if os.path.isfile(f"sams/{acc}.sam"):
            with open(f"sams/{acc}.sam", "r", encoding="utf-8") as sam_file:
                lines = len(sam_file.read().split("\n"))
                if lines > 502:
                    passed.append(acc)

    return passed


def add_sample(agg, file, samp):
    """
    This function adds the pased sample data to the passed file

    Parameters:
    agg - aggregate file - open file handle
    file - name of the sample file - str
    samp - sample accession - str

    Functionality:
        Opens the sample file and writes date from it to the aggreagate file

    Returns
    """

    with open(file, "r", encoding="utf-8") as samp_fh:
        if file.endswith(".tsv"):
            agg.write(samp)
            agg.write("\n")
        agg.write(samp_fh.read())
        if file.endswith(".tsv"):
            agg.write("\n--------\n")


def check_if_present(agg, redo, file, samp):
    """
    This function checks if the sample is present in the aggregated file.

    Parameters:
    agg - aggregate file - open file handle
    redo - boolean to indicate if samples are to be reprocessed - bool
    file - name of the sample file - str
    samp - sample accession - str

    Functionality:
        Parses the aggreagate file data from the current sample.  If not found
        the data is added to the aggregate file.  If it is found and redo is
        True, re_write is set to true.

    Returns re_write
    """

    agg.seek(0)
    present = samp in agg.read()
    re_write = False

    if redo and present:
        re_write = True
    elif not present:
        add_sample(agg, file, samp)

    return re_write


def re_write_tsv_file(re_write_file, samp, file):
    """
    This function takes the variant call or lineage call tsv file and adds the
    new variant calls as necessary.

    Parameters:
    re_write_file - aggregate file - str
    samp - sample accession - str
    file - name of the sample file - str

    Functionality:
        Reads the current aggregate file and re-writes it without the old data
        for the sample and with the new data

    Returns
    """

    old_file = ""
    new_file = ""

    with open(re_write_file, "r", encoding="utf-8") as agg:
        old_file = agg.read()
    old_split = old_file.split("\n--------\n")

    for data in old_split:
        if (not data.startswith(samp)) and data.strip():
            new_file += data
            new_file += "\n--------\n"

    with open(re_write_file, "w", encoding="utf-8") as agg:
        agg.write(new_file)
        with open(file, "r", encoding="utf-8") as samp_fh:
            agg.write(samp)
            agg.write("\n")
            agg.write(samp_fh.read())
            agg.write("\n--------\n")


def re_write_consensus_file(con_file, samp, file):
    """
    This function re-writes the consensus file if necessary. This function is
    separate from the more general re_write_tsv_file() because the consensus
    is in fasta format.

    Parameters:
    con_file - aggregate file - str
    samp - sample accession - str
    file - name of the sample file - str

    Functionality:
        Reads the current aggregate file and re-writes it without the old data
        for the sample and with the new data

    Returns
    """

    old_file = ""
    new_file = ""

    with open(con_file, "r", encoding="utf-8") as agg:
        old_file = agg.read()

    old_split = old_file.split(">")

    for data in old_split:
        if (not samp in data) and data.strip():
            new_file += ">"
            new_file += data

    with open(con_file, "w", encoding="utf-8") as agg:
        agg.write(new_file)
        with open(file, "r", encoding="utf-8") as samp_fh:
            agg.write(samp_fh.read())


def aggregate_endpoints(vc_list, con_list, lin_list, redo) -> int:
    """
    Called to aggregate the individual sample endpoints.

    Parameters:
    vc_list - list files for variant calls - list
    con_list - list files for consensus - list
    lin_list - list files for lineages - list
    redo - boolean for the samples being reprocessed - bool

    Functionality:
        Adds sample data to the aggregate files unless it is
        already present and reprocessing isn't being done

    Returns 0 if successful.
    """

    vc_file = "endpoints/VCs.tsv"
    con_file = "endpoints/Consensus.fa"
    lineage_file = "endpoints/Lineages.tsv"

    ####################
    # Iterate through variant calls, adding to summary file if not yet present

    for file in vc_list:
        samp = file.split("/")[1].split(".")[0]

        with open(vc_file, "a+", encoding="utf-8") as agg:
            re_write = check_if_present(agg, redo, file, samp)

        if re_write:
            re_write_tsv_file(vc_file, samp, file)

    ####################
    # Iterate through consensus definitions, adding to summary file if not yet
    # present

    for file in con_list:
        samp = file.split("/")[1].split(".")[0]

        with open(con_file, "a+", encoding="utf-8") as agg:
            re_write = check_if_present(agg, redo, file, samp)

        if re_write:
            re_write_consensus_file(con_file, samp, file)

    ####################
    # Iterate through lineages, adding to summary file if not yet present

    for file in lin_list:
        samp = file.split("/")[1].split(".")[0]

        with open(lineage_file, "a+", encoding="utf-8") as agg:
            re_write = check_if_present(agg, redo, file, samp)

        if re_write:
            re_write_tsv_file(lineage_file, samp, file)

    return 0
