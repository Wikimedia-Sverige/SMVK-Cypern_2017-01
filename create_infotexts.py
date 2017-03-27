#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Create info files for batch SMVK-Cypern_2017-01
This is step 2 in the batchupload process for SMVK-Cypern_2017-01. Step 1. was to transform the Excel-metadata to
JSON-file ´SMVK-Cypern_2017-01_metadata.json´ and add new filenames, SMVK-MM-link and add Fotonummer as key..

Outputs <Fotonummer>.info files in a subdirectory ./infofiles/
"""

import json
import re
import pandas as pd
import batchupload.helpers as helpers

people_mapping_file = open("./people_mappings.json")
people_mapping = json.loads(people_mapping_file.read())


def load_places_mapping():
    """
    Read  wikitable html and return a dictionary
    :return: dictionary
    """
    kw_maps_url = "https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Cypern_places"
    places = pd.read_html(kw_maps_url, attrs={"class": "wikitable sortable"}, header=0)

    places_df = places[0]  # read_html returns a list of found tables, each of which as a dataframe
    places_df = places_df.set_index("Nyckelord")
    places_df.columns = ["freq", "commons", "wikidata"]

    places_dict = {}

    for index, row in places_df.iterrows():
        places_dict[index] = {}
        places_dict[index]["commons"] = row["commons"]
        places_dict[index]["wikidata"] = row["wikidata"]

    return places_dict


def create_commons_filename(metadata, fotonr):
    """
    Transform original filename into Wikimedia commons style filename.

    See https://phabricator.wikimedia.org/T156612 for definition.
    Note: the returned filename does not include file extension e.g. '.tif'

    :param metadata: dictionary
    :param fotonr: string representing the <Fotonummer> field in the metadata
    :return: string
    """
    if not metadata[fotonr]["Beskrivning"] == "":
        cleaned_fname = helpers.format_filename(metadata[fotonr]["Beskrivning"], "SMVK-MM-Cypern",
                                                metadata[fotonr]["Fotonummer"])
        # print("Fname using BatchUploadTools: {}".format(cleaned_fname))
    else:
        # TODO: Generate better descriptions, see https://phabricator.wikimedia.org/T158945
        beskr = "Svenska Cypernexpeditionen 1927-1931"
        cleaned_fname = helpers.format_filename(beskr, "SMVK-MM-Cypern", metadata[fotonr]["Fotonummer"])

    return cleaned_fname  # Assuming extension will be added på PrepUpload


def load_json_metadata(infile):
    """
    Load metadata json blob as dictionary for further processing.
    :infile: created with ´metadata_to_json_and_fnamesmap.py´
    :returns: dictionary with <Fotonummer> as keys e.g. `C03643` for image file `C03643.tif´
    """
    metadata = json.load(open(infile))

    # print("metadata item C01427: {}".format(metadata["C01427"]))

    return metadata


def create_people_mapping_wikitable(people_mapping):
    """
    Transform dictionary containing people mapping to wikitable.

    :param people_mapping: json dictionary
    :return: string
    """
    table = ""
    table += """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! name
! commons
! wikidata
|-\n"""
    for full_name in people_mapping:
        table += "| " + people_mapping[full_name]["name"] + "\n"
        if "commons" in people_mapping[full_name].keys():
            better_commons_link = re.sub(r"\[\[Category", "[[:Category", people_mapping[full_name]["commons"])
            table += "| " + better_commons_link + "\n"
        else:
            table += "| -\n"
        if "wikidata" in people_mapping[full_name].keys():
            table += "| " + people_mapping[full_name]["wikidata"] + "\n"
        else:
            table += "| -\n"
        table += "|-\n"
    table += "-}\n"

    return table


def create_smvk_mm_link(item):
    """Populates template SMVK-MM-link and appends to dictionary."""
    smvk_link = "{{{{SMVK-MM-LINK|{postnr}|{fotonr}}}}}".format(postnr=item["Postnummer"], fotonr=item["Fotonummer"])

    return smvk_link


def select_best_mapping_for_depicted_person(flipped_name):
    """
    Lookup available mappings for a string respresenting a name and return best choice.
    The priority order is wikidata item < commons category < the name only

    :flipped_name: string representing full name turned around from
        e.g. "surname, given name" -> "given name surname"
        note that give_name is normally one word e.g. "Erfraim"
    :return:  string representing the selcted mapping value
    """
    if "wikidata" in people_mapping[flipped_name].keys():
        return people_mapping[flipped_name]["wikidata"]
    elif "commons" in people_mapping[flipped_name].keys():
        return people_mapping[flipped_name]["commons"]
    else:
        return people_mapping[flipped_name]["name"]


def extract_mappings_from_list_of_depicted_people(flipped_names):
    """
    Pass each name in a list of names to mapping function.

    :param flipped_names: string with full names turned around from e.g. "surname, given name" -> "given name surename"
    :return: a string represention of several names mapped to either wikidata, commons or the names only
    """

    out_string = ""
    for name in flipped_names:
        selected_mapping = select_best_mapping_for_depicted_person(name)
        out_string += selected_mapping + "/"
    mapped_names = out_string.rstrip("/")
    return mapped_names


def extract_mapping_of_depicted_person(flipped_name):
    """
        :flipped_name: string representing full name turned around from e.g.
        "surname, given name" -> "given name surename"
        :return: string representation of a name mapped to either wikidata, commons or the name only
        """
    mapped_name = select_best_mapping_for_depicted_person(flipped_name)
    return mapped_name


def map_depicted_person_field(name_string_or_list):
    """
        :name_string_or_list: string representing one full name or series of full names (of faulty)
        :return: a string of either one mapped name or several mapped names
        """
    words = name_string_or_list.split(", ")
    span = 2
    joined_words = [", ".join(words[i:i + span]) for i in range(0, len(words), span)]
    # print("joined_words: {}".format(joined_words))

    if len(joined_words) == 1:
        flipped_name = helpers.flip_name(joined_words[0])
        # print("flipped_name: {}".format(flipped_name))
        depicted_people_value = extract_mapping_of_depicted_person(flipped_name)
        return depicted_people_value

    elif len(joined_words) > 1:
        flipped_names = helpers.flip_names(joined_words)
        # print("flipped_names: {}".format(flipped_names))
        depicted_people_value = extract_mappings_from_list_of_depicted_people(flipped_names)
        return depicted_people_value

    else:
        # TODO: add logic for maintanence category for faulty depicted people field
        print("<Personnamn / avbildad> doesn't seem to be even full names: {}".format(name_string_or_list))
        return name_string_or_list


def generate_infobox_template(item, places):
    """Takes one item from metadata dictionary and constructs the infobox template.
    :item: one metadata row for one photo
    :returns: infobox for the item as a string
    """

    infobox = ""
    infobox += "{{Photograph \n"

    # 22 characters from start of string to '='
    if not item["Personnamn / fotograf"] == "":
        infobox += "| photographer       =  {{Creator:John Lindros}}\n"
    else:
        infobox += "| photographer       = \n"

    infobox += "| title               =\n"

    infobox += "| description        = {{sv| "
    if not item["Beskrivning"] == "":
        # print("item['Beskrivning']: {}".format(item["Beskrivning"]))
        cleaned_beskrivning = re.sub(" Svenska Cypernexpeditionen\.?", "", item["Beskrivning"])
        infobox += cleaned_beskrivning
        if not cleaned_beskrivning.endswith("."):
            infobox += "."
    infobox += " Svenska Cypernexpeditionen 1927-1931."
    if not item["Nyckelord"] == "" and not item["Nyckelord"] == "Svenska Cypernexpeditionen":
        infobox += "<br /> ''Nyckelord:''\n" + item["Nyckelord"]
    infobox += "}}\n"
    infobox += "{{en|The Swedish Cyprus expedition 1927-1931}}"
    infobox += "\n"

    infobox += "| depicted people    = "
    if not item["Personnamn / avbildad"] == "":
        name_string_or_list = item["Personnamn / avbildad"]
        mapped_depicted_person_field = map_depicted_person_field(name_string_or_list)
        infobox += mapped_depicted_person_field + "\n"

    else:
        infobox += "\n"

    infobox += "| depicted place     = "
    if item["Ort, foto"] in places:
        if not places[item["Ort, foto"]]["wikidata"] == "-":
            # print("item['Ort, foto']: {} places: {}".format(item["Ort, foto"], places[item["Ort, foto"]]["wikidata"]))
            infobox += "{{city|1=" + places[item["Ort, foto"]]["wikidata"][2:] + "|link=wikidata}}"
        else:
            # print("item['Ort, foto']: {} places: {}".format(item["Ort, foto"], places[item["Ort, foto"]]["wikidata"]))
            infobox += "{{city|1=" + places[item["Ort, foto"]]["commons"] + "|link=commons}}"
    infobox += "\n"

    infobox += "| date               = "
    if not item["Fotodatum"] == "":
        infobox += str(item["Fotodatum"])
    infobox += "\n"

    infobox += "| medium             = " + "\n"

    infobox += "| dimensions         = " + "\n"

    infobox += "| institution        = {{Institution:Statens museer för världskultur}}" + "\n"

    infobox += "| department         = [[:d:Q1331646|Medelhavsmuseet]]" + "\n"

    infobox += "| references         = " + "\n"

    infobox += "| objects history    = " + "\n"

    infobox += "| exhibition history = " + "\n"

    infobox += "| credit line        = " + "\n"

    infobox += "| inscriptions       = " + "\n"

    infobox += "| notes              = " + "\n"

    infobox += "| accession number   = " + create_smvk_mm_link(item) + "\n"

    infobox += "| source             = " + "The original image file was recieved from SMVK with the following filename:"

    infobox += "<br />'''" + item["Fotonummer"] + ".tif'''\n{{SMVK cooperation project|COH}}\n"

    infobox += "| permission         = {{cc-zero}}\n"

    infobox += "| other_versions     = \n"

    infobox += "}}\n"

    return infobox


def generate_content_cats(item):
    """Takes one item from metadata dictionary and constructs the meta-categories.
    :item: one metadata row for one photo
    :returns: meta-categories as string
    """
    # TODO: write logic for content-categories [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/10]
    # TODO: make depicted people with commons cat be added to content cats
    pass


def generate_meta_cats(item):
    """Takes one item from metadata dictionary and constructs the meta-categories.
    :item: one metadata row for one photo
    :returns meta-categories as string
    """
    # TODO: write logic for meta-categories e.g. maintanence categories
    # [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/12]
    # see https://phabricator.wikimedia.org/T156612#3008806 on lacking description
    pass


def main():
    """Creation of the infoxtext, i.e. wikitext, that goes along with an uploaded image to Commons.
    
    :metadata_json: created with script `metadata_to_json_and_fnamesmap.py
    """
    metadata_json = "SMVK-Cypern_2017-01_metadata.json"
    outpath = "./infofiles/"

    people = create_people_mapping_wikitable(people_mapping)
    # print(people + "\n")

    places = load_places_mapping()
    # print(places)

    metadata = load_json_metadata(metadata_json)
    for fotonr in metadata:
        full_infotext = ""
        outfile = open(outpath + fotonr + ".info", "w")

        commons_filename = create_commons_filename(metadata, fotonr)
        print("New filename: {}".format(commons_filename))

        infobox = generate_infobox_template(metadata[fotonr], places)

        # print(infobox)
        full_infotext += infobox + "\n"

        # content_cats = generate_content_cats(metadata[fotonr])
        # full_infotext += content_cats + "\n" # content cats can also be added by depicted persons

        # meta_cats = generate_meta_cats(metadata[fotonr])
        # full_infotext += meta_cats

        print(full_infotext + "\n--------------\n")
        # outfile.write(infotext)
        outfile.close()


if __name__ == '__main__':
    main()
