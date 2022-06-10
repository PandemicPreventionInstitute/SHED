"""
Writen by Devon Gregory
This script has functions to query NCBI's SRA database to obtain sample
metadata for samples matching the search string 'SARS-CoV-2 wastewater'.
Last edited on 6-7-22
"""

import os
import sys
import subprocess
import xml.parsers.expat
import json
import shutil


def sra_query(search_str: str, date_stamp: str) -> int:
    """
    Called to query NCBI's SRA and collect metadata for the query results.

    Parameters:
    search_str - string for the query - str
    date_stamp - timestamp of current query - str

    Functionality:
        curl is used to download the html results for the query.
        The html is then parsed to find the MDID and key of the specific
        query for downloading the metadata, also using using curl.  Files
        are tagged with the date stamp.

        Searches returning no results (and maybe only 1 result) will cause
        a program exit.

        Return: 0 if no exceptions were raised
    """

    subprocess.run(
        [
            "curl -A 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0)"
            "Gecko/20100101 Firefox/50.0' -L --alt-svc ''"
            "--anyauth -b ncbi"
            f"'https://www.ncbi.nlm.nih.gov/sra/?term={search_str}'"
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
            "curl  'https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?"
            f"save=efetch&rettype=runinfo&db=sra&WebEnv=MCID{mcid}&query_key={key}'"
            "-L -o sra_data_{date_stamp}.csv"
        ],
        shell=True,
        check=True,
    )
    subprocess.run(
        [
            "curl 'https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?"
            f"save=efetch&rettype=exp&db=sra&WebEnv=MCID_{mcid}&query_key={key}'"
            " -L -o sra_meta_{date_stamp}.xml"
        ],
        shell=True,
        check=True,
    )
    return 0


def get_primer_bed(primers_str: str) -> str:
    """
    Called to determine the proper primer bed based on the str passed.

    Parameters:
    primers_str - string of potential primer info - str

    Functionality:
        parses the passed string for specific keywords to determine the most
        likely primers used in the sequencing.


    Returns string of the bed file
    """

    with open("data/primer_mapping.json", encoding="utf-8") as _primer_map_json:
        _primer_map_dict = json.load(_primer_map_json)

    # keys = _primer_map_dict.keys()
    # contains_key = keys in primers_str

    # if sum(contains_key) == 1:  # if exactly one match

    # bed = bed.get(keys[contains_key], "Unknown")

    # # If the match is a subdict, iterate through it  match there necessary
    # while isinstance(bed, dict):

    # keys = bed.keys()
    # contains_key = keys in primers_str
    # bed = bed.get(keys[contains_key], "Unknown")

    # else:

    # bed = "Unknown"

    bed = "Unknown"
    matching_dict = _primer_map_dict
    while isinstance(matching_dict, dict) and bed == "Unknown":
        for key in matching_dict:
            if key in primers_str:
                if isinstance(_primer_map_dict[key], str):
                    bed = _primer_map_dict[key]
                    break  # multiple keys may be present in primers_str, match the first key only
                matching_dict = matching_dict[key]
            else:
                try:
                    bed = matching_dict["Other"]
                except KeyError:
                    pass

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
            for elems in element_strs[2:]:
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


def end_ele_fun(name, element_strs, elements_dict, out_fh, lite_out_fh):
    """
    Called to perform the actions and logic of dealing with the end
    of an xml element.

    Parameters:
    name - name of the element - str
    element_strs - list of the elements/subelements - list
    elements_dict - dict to collect metadata from elements - dict
    out_fh - file to write out all metadata - file object
    lite_out_fh - file to write out select metadata - file object

    Functionality:
        parses the passed element info and updates/writes out metadata

    Returns elements_dict
    """

    if element_strs and len(element_strs) < 2:
        out_fh.write("\n")
        lite_out_fh.write(
            f"{elements_dict['accession']}\t{elements_dict['date']}\t{elements_dict['loc']}\t"
        )
        if elements_dict["primers"]:
            lite_out_fh.write(get_primer_bed(" ".join(elements_dict["primers"])))
        else:
            lite_out_fh.write("Unknown")
        lite_out_fh.write("\t")
        lite_out_fh.write(" ".join(elements_dict["primers"]))
        lite_out_fh.write("\n")
        elements_dict["accession"] = ""
        elements_dict["date"] = ""
        elements_dict["loc"] = ""
        elements_dict["primers"] = []

    return elements_dict


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

    if len(element_strs) > 1:
        for elems in element_strs[1:]:
            out_fh.write("    ")
    out_fh.write(data)
    out_fh.write("\n")
    if flags["loc"]:
        if element_strs[-1] == "VALUE":
            if elements_dict["loc"]:
                elements_dict["loc"] += ", " + data
            else:
                elements_dict["loc"] = data
        flags["loc"] = False
    if element_strs[-1] == "TAG" and (
        data == "geo_loc_name"
        or data == "geo loc name"
        or "geographic location" in data
    ):
        flags["loc"] = True
    if flags["date"]:
        if element_strs[-1] == "VALUE":
            elements_dict["date"] = data
        flags["date"] = False
    if element_strs[-1] == "TAG" and (data in ("collection_date", "collection date")):
        flags["date"] = True
    if "SNAP" in data.upper():
        if "ADD" in data.upper():
            elements_dict["primers"].append("SNAPadd")
        else:
            elements_dict["primers"].append("SNAP")
    if "SWIFT" in data.upper():
        elements_dict["primers"].append("SNAP")
    if "QIASEQ" in data.upper():
        elements_dict["primers"].append("QiaSeq")
    if "NEBNEXT" in data.upper():
        elements_dict["primers"].append("NEBNext")
        if "VARSKIP" in data.upper():
            elements_dict["primers"].append("VarSkip")
        if "LONG" in data.upper():
            elements_dict["primers"].append("Long")
        if "SHORT" in data.upper():
            elements_dict["primers"].append("Short")
        if "V2" in data.upper():
            elements_dict["primers"].append("V2")
    if "ARTIC" in data.upper():
        if "V3" in data.upper():
            elements_dict["primers"].append("ArticV3")
        elif "V4.1" in data.upper():
            elements_dict["primers"].append("ArticV4.1")
        elif "V4" in data.upper():
            elements_dict["primers"].append("ArticV4")
        else:
            elements_dict["primers"].append("Artic")
    if "PRJNA715712" in data:
        elements_dict["primers"].append("Spike-Amps")
    if "PRJNA748354" in data:
        elements_dict["primers"].append("Spike-Amps")
    if "FISHER" in data.upper() or "ION AMPLISEQ" in data.upper():
        elements_dict["primers"].append("IonAmpliSeq")
    if "PARAGON" in data.upper():
        elements_dict["primers"].append("Paragon")

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
                    element_strs.pop()
                    end_ele_fun(name, element_strs, elements_dict, out_fh, lite_out_fh)

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

    Parameters:
    sample_accs - accession list for the SRA samples - list

    Functionality:
        Checks the fastqs subfolder for single or paired qced fastq files,
        then checks the qc json for sufficient passed reads to conintue.
        Currently requires over 500 passed reads. returns list of passed samples

    Returns list of past accs
    """

    passed = []
    for acc in sample_accs:
        pe_files = [f"fastqs/{acc}_1.qc.fq", f"fastqs/{acc}_2.qc.fq"]
        se_file = f"fastqs/{acc}.qc.fq"
        if os.path.isfile(pe_files[0]) and os.path.isfile(pe_files[1]):
            with open(f"fastqs/{acc}.pe.json", "r", encoding="utf-8") as json_fh:
                json_as_dict = json.load(json_fh)
                if json_as_dict["filtering_result"]["passed_filter_reads"] > 500:
                    passed.append(acc)
        elif os.path.isfile(se_file):
            with open(f"fastqs/{acc}.se.json", "r", encoding="utf-8") as json_fh:
                json_as_dict = json.load(json_fh)
                if json_as_dict["filtering_result"]["passed_filter_reads"] > 500:
                    passed.append(acc)

    return passed


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

    for file in vc_list:
        samp = file.split("/")[1].split(".")[0]
        re_write = False
        with open("endpoints/VCs.tsv", "a+") as agg:
            agg.seek(0)
            present = samp in agg.read()
            if redo and present:
                re_write = True
            elif not present:
                with open(file, "r", encoding="utf-8") as samp_fh:
                    agg.write(samp)
                    agg.write("\n")
                    agg.write(samp_fh.read())
                    agg.write("\n--------\n")
        if re_write:
            old_file = ""
            new_file = ""
            with open("endpoints/VCs.tsv", "r", encoding="utf-8") as agg:
                old_file = agg.read()
            old_split = old_file.split("\n--------\n")
            for data in old_split:
                if (not data.startswith(samp)) and data.strip():
                    new_file += data
                    new_file += "\n--------\n"
            with open("endpoints/VCs.tsv", "w", encoding="utf-8") as agg:
                agg.write(new_file)
                with open(file, "r", encoding="utf-8") as samp_fh:
                    agg.write(samp)
                    agg.write("\n")
                    agg.write(samp_fh.read())
                    agg.write("\n--------\n")

    for file in con_list:
        samp = file.split("/")[1].split(".")[0]
        re_write = False
        with open("endpoints/Consensus.fa", "a+") as agg:
            agg.seek(0)
            present = samp in agg.read()
            if redo and present:
                re_write = True
            elif not present:
                with open(file, "r", encoding="utf-8") as samp_fh:
                    agg.write(samp_fh.read())
        if re_write:
            old_file = ""
            new_file = ""
            with open("endpoints/Consensus.fa", "r", encoding="utf-8") as agg:
                old_file = agg.read()
            old_split = old_file.split(">")
            for data in old_split:
                if (not samp in data) and data.strip():
                    new_file += ">"
                    new_file += data
            with open("endpoints/Consensus.fa", "w", encoding="utf-8") as agg:
                agg.write(new_file)
                with open(file, "r", encoding="utf-8") as samp_fh:
                    agg.write(samp_fh.read())

    for file in lin_list:
        samp = file.split("/")[1].split(".")[0]
        re_write = False
        with open("endpoints/Lineages.tsv", "a+") as agg:
            agg.seek(0)
            present = samp in agg.read()
            if redo and present:
                re_write = True
            elif not present:
                with open(file, "r", encoding="utf-8") as samp_fh:
                    agg.write(samp)
                    agg.write("\n")
                    agg.write(samp_fh.read())
                    agg.write("\n--------\n")
        if re_write:
            old_file = ""
            new_file = ""
            with open("endpoints/Lineages.tsv", "r", encoding="utf-8") as agg:
                old_file = agg.read()
            old_split = old_file.split("\n--------\n")
            for data in old_split:
                if (not data.startswith(samp)) and data.strip():
                    new_file += data
                    new_file += "\n--------\n"
            with open("endpoints/Lineages.tsv", "w", encoding="utf-8") as agg:
                agg.write(new_file)
                with open(file, "r", encoding="utf-8") as samp_fh:
                    agg.write(samp)
                    agg.write("\n")
                    agg.write(samp_fh.read())
                    agg.write("\n--------\n")

    return 0
