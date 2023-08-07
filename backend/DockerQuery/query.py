"""
Writen by Devon Gregory
This script has functions called by the snakefiles to query NCBI'
SRA and download and process the files for the results.
Last edited on 6-22-23
"""

import os
import sys
import subprocess
import xml.parsers.expat
import json
import datetime


def sra_query(search_str: str, date_stamp: str, overwrite: bool) -> int:
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

    if overwrite or not os.path.isfile(f"search_results_{date_stamp}.html"):
        subprocess.run(
            [
                "curl -A 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) "
                "Gecko/20100101 Firefox/50.0' -L "
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
    if overwrite or not os.path.isfile(f"sra_data_{date_stamp}.csv"):
        subprocess.run(
            [
                "curl 'https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/sra-db-be."
                f"cgi?rettype=runinfo&WebEnv=MCID_{mcid}&query_key={key}' "
                f"-L -o sra_data_{date_stamp}.csv"
            ],
            shell=True,
            check=True,
        )
    if overwrite or not os.path.isfile(f"sra_meta_{date_stamp}.xml"):
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
        mapping_file, "r", encoding="utf-8"
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


def parse_xml_meta(date_stamp: str, overwrite: bool) -> int:
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

    if overwrite or not os.path.isfile(f"sra_meta_collect_{date_stamp}.tsv"):
        with open(
            f"sra_meta_{date_stamp}.xml", "r", encoding="utf-8"
        ) as full_meta_in_fh:
            with open(f"sra_meta_{date_stamp}.txt", "w", encoding="utf-8") as out_fh:
                with open(
                    f"sra_meta_collect_{date_stamp}.tsv", "w", encoding="utf-8"
                ) as lite_out_fh:
                    lite_out_fh.write(
                        "Accession\tsample_collection_date\tgeo_loc\tprimers\n"
                    )
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

    return 0


if __name__ == "__main__":

    try:
        aws_key = os.environ["AWS_ACCESS_KEY_ID"]
        aws_secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    except KeyError:
        print("s3 keys not found")

    subprocess.run(
    [
        "aws s3 sync s3://ppi-dev/shed/Processed_Accessions/ ."
    ],
    shell=True,
    check=True,
    )

    try:
        query_str = os.environ["query_str"]
    except KeyError:
        print("query string not found, using default 'sars-cov-2+wastewater+usa'")
        query_str = 'sars-cov-2+wastewater+usa'

    print(f"query string is : {query_str}")

    try:
        split_num = int(os.environ["split_num"])
    except:
        split_num = 20

    try:
        max_count = int(os.environ["max_count"])
    except:
        max_count = 200


    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H.%M.%S")
    # timestamp = "2023-06-21_18.44.08"




    sra_query(query_str, timestamp, False)
    parse_xml_meta(timestamp, False)

    processed_accs = []
    for file in os.listdir(os.getcwd()):
        if file.endswith("processed_SRA_Accessions.txt"):
            with open(file, "r") as in_fh:
                for line in in_fh:
                    processed_accs.append(line.strip().split(".")[0])


    with open(f"sra_meta_collect_{timestamp}.tsv", "r") as meta_in_hf:
        header = meta_in_hf.readline()
        file_finished = 0
        for i in range(0, split_num):
            if file_finished == 1:
                break
            with open(f"sra_meta_collect_{timestamp}_{i}.tsv", "w") as meta_out_fh:
                meta_out_fh.write(header)
                count = 0
                for line in meta_in_hf:
                    if not line.split("\t")[0] in processed_accs:
                        meta_out_fh.write(line)
                        count += 1
                    if count >= max_count:
                        break
                if count < max_count:
                    file_finished = 1

            subprocess.run(
            [
                f"aws s3 cp sra_meta_collect_{timestamp}_{i}.tsv s3://ppi-dev/shed/task_metadata_files/sra_meta_collect_{timestamp}_{i}.tsv"
            ],
            shell=True,
            check=True,
            )

            with open(f"{i}.json", "w") as json_out:
                with open("overide_template.json", "r") as json_temp:
                    json_out.write(json_temp.read().replace("count_string", str(i)).replace("timestamp_string", timestamp))


            rt_str1 = "--region us-east-1 --task-definition arn:aws:ecs:us-east-1:661084887439:task-definition/shed-be-process-test:4"
            rt_str2 = "--cluster arn:aws:ecs:us-east-1:661084887439:cluster/ppi-shed --launch-type=FARGATE --network-configuration"
            network_str = '{ "awsvpcConfiguration": { "assignPublicIp":"ENABLED", "securityGroups": ["sg-0e582321f95c2a606"], "subnets": ["subnet-0f0cf509487d7754c"]}}'

            subprocess.run(
            [
                f"aws ecs run-task {rt_str1} --overrides=file://{i}.json {rt_str2} '{network_str}' > {i}.rundef"
            ],
            shell=True,
            check=True,
            )

