#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Create info files for batch SMVK-Cypern_2017-01
This is step 2 in the batchupload process for SMVK-Cypern_2017-01. Step 1. was to transform the Excel-metadata to
JSON-file ´SMVK-Cypern_2017-01_metadata.json´ and add new filenames, SMVK-MM-link and add Fotonummer as key..

Outputs <Fotonummer>.info files in a subdirectory ./infofiles/
"""

import os
import json
import re
import pandas as pd
import batchupload.helpers as helpers

people_mapping_string = """{
	"John Lindros": {
	    "name":"John Lindros",
		"commons": "[[Category:John Lindros|John Lindros]]",
		"wikidata": "[[:d:Q5957823|John Lindros]]"
	},
	"Lazaros Kristos": {
		"name": "Lazaros Kristos"
	},
	"Alfred Westholm": {
	    "name":"Alfred Westholm",
		"commons": "[[Category:Alfred Westholm|Alfred Westholm]]",
		"wikidata": "[[:d:Q6238028|Alfred Westholm]]"
	},
	"Erik Sjökvist": {
	    "name":"Erik Sjöqvist",
		"commons": "[[Category:Erik Sjöqvist|Erik Sjöqvist]]",
		"wikidata": "[[:d:Q5388837|Erik Sjöqvist]]"
	},
	"Erik Sjöqvist": {
	    "name":"Erik Sjöqvist",
		"commons": "[[Category:Erik Sjöqvist|Erik Sjöqvist]]",
		"wikidata": "[[:d:Q5388837|Erik Sjöqvist]]"
	},
	"Einar Gjerstad": {
	    "name":"Einar Gjerstad",
		"commons": "[[Category:Einar Gjerstad|Einar Gjerstad]]",
		"wikidata": "[[:d:Q481299|Einar Gjerstad]]"
	},
	"Lazaros Giorkos": {
		"name": "Lazaros Giorkos"
	},
	"Stefan Gjerstad": {
		"name": "Stefan Gjerstad"
	},
	"Vivi Gjerstad": {
		"name": "Vivi Gjerstad"
	},
	"Gudrun Otterman": {
		"name":"Gudrun Otterman"
	},
	"Martin Gjerstad": {
	    "name":"Martin Gjerstad",
		"commons": "[[Category:Martin Gjerstad|Martin Gjerstad]]",
		"wikidata": "[[d:Q16632979|Martin Gjerstad]]"
	},
	"Knut Thyberg": {
	    "name":"Knut Thyberg",
		"commons": "[[Category:Knut Thyberg|Knut Thyberg]]",
		"wikidata": "[[:d:Q16633505|Knut Thyberg]]"
	},
	"Rosa Lindros": {
		"name":"Rosa Lindros"
	},
	"Ernst Kjellberg": {
	    "name":"Ernst Kjellberg",
		"commons": "[[Category:Ernst Kjellberg|Ernst Kjellberg]]",
		"wikidata": "[[:d:Q5911946|Ernst Kjellberg]]"
	},
	"Bror Millberg": {
		"name": "Bror Millberg"
	}
}"""

people_mapping = json.loads(people_mapping_string)

def load_places_mapping():
    """Reads wikitable html and returns a dictionary"""
    kw_maps_url = "https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Cypern_places"
    places = pd.read_html(kw_maps_url, attrs={"class": "wikitable sortable"}, header=0)

    places_df = places[0] # read_html returns a list of found tables, each of which as a dataframe
    places_df = places_df.set_index("Nyckelord")
    places_df.columns = ["freq","commons","wikidata"]

    places_dict = {}

    for index, row in places_df.iterrows():
        places_dict[index] = {}
        places_dict[index]["commons"] = row["commons"]
        places_dict[index]["wikidata"] = row["wikidata"]

    return places_dict

def load_json_metadata(infile):
    """Load metadata json blob created with ´metadata_to_json_and_fnamesmap.py´"""
    metadata = json.load(open(infile))

    #print("metadata item C01427: {}".format(metadata["C01427"]))

    return metadata

def create_people_mapping_wikitable(people_mapping):
    # TODO: create logic for people mapping wikitable
    pass

def generate_infobox_template(item, places):
    """Takes one item from metadata dictionary and constructs the infobox template.

    Return: item infobox as string
    """
    # TODO: write infobox logic based on https://phabricator.wikimedia.org/T156612 [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/11]

    depicted_people_content_category_string = "" # to keep track of and add unused commons categories

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
        #print("item['Beskrivning']: {}".format(item["Beskrivning"]))
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

    def select_best_mapping_for_depicted_person(flipped_name):
        if "wikidata" in people_mapping[flipped_name].keys():
            return people_mapping[flipped_name]["wikidata"]
        else:
            if "commons" in people_mapping[flipped_name].keys():
                return people_mapping[flipped_name]["commons"]
            else:
                return people_mapping[flipped_name]["name"]


    def extract_mappings_from_list_of_depicted_people(flipped_names):
        out_string = ""
        for name in flipped_names:
            selected_mapping = select_best_mapping_for_depicted_person(name)
            out_string += selected_mapping + "/"
        mapped_names = out_string.rstrip("/")
        return mapped_names

    def extract_mapping_of_depicted_person(flipped_name):
            mapped_name = select_best_mapping_for_depicted_person(flipped_name)
            return mapped_name


    def map_depicted_person_field(name_string_or_list):

        words = name_string_or_list.split(", ")
        span = 2
        joined_words = [", ".join(words[i:i + span]) for i in range(0, len(words), span)]
        print("joined_words: {}".format(joined_words))

        if len(joined_words) == 1:
            flipped_name = helpers.flip_name(joined_words[0])
            print("flipped_name: {}".format(flipped_name))
            depicted_people_value = extract_mapping_of_depicted_person(flipped_name)
            return depicted_people_value

        elif len(joined_words) >1:
            flipped_names = helpers.flip_names(joined_words)
            print("flipped_names: {}".format(flipped_names))
            depicted_people_value = extract_mappings_from_list_of_depicted_people(flipped_names)
            return depicted_people_value

        else:
            # TODO: add logic for maintanence category for faulty depicted people field
            print("<Personnamn / avbildad> doesn't seem to be even full names: {}".format(name_string_or_list))
            return name_string_or_list




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
            #print("item['Ort, foto']: {} places: {}".format(item["Ort, foto"], places[item["Ort, foto"]]["wikidata"]))
            infobox += "{{city|1=" + places[item["Ort, foto"]]["wikidata"][2:] + "|link=wikidata}}"
        else:
            #print("item['Ort, foto']: {} places: {}".format(item["Ort, foto"], places[item["Ort, foto"]]["wikidata"]))
            infobox += "{{city|1=" + places[item["Ort, foto"]]["commons"] + "|link=commons}}"
    infobox += "\n"

    infobox += "| date               = "
    if not item["Fotodatum"] == "":
        infobox += str(item["Fotodatum"])
    infobox += "\n"


#  |date               = <Fotodatum>
#  |medium             =
#  |dimensions         =
#  |institution        = {{Institution:Statens museer för världskultur}}
#  |department         = [[:d:Q1331646|Medelhavsmuseet]]
#  |references         =
#  |object history     =
#  |exhibition history =
#  |credit line        =
#  |inscriptions       =
#  |notes              =
#  |accession number   = {{SMVK-MM-link|<Länk[last digits]>|<Fotonummer>}}
#  |source             = The original image file was recieved from SMVK with the following filename:  <br />
# '''<Fotonummer>.tif''' // Double check this!
# {{SMVK cooperation project|COH}}
#  |permission         = {{cc-zero}}
#  |other_versions     =
# }}
#     """
    print()
    print(infobox)

    infobox += depicted_people_content_category_string + "\n"

    return infobox

def generate_content_cats(item):
    """Takes one item from metadata dictionary and constructs the meta-categories.

        Return: meta-categories as string"""
    # TODO: write logic for content-categories [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/10]
    pass

def generate_meta_cats(item):
    """Takes one item from metadata dictionary and constructs the meta-categories.

    Return: meta-categories as string"""
    # TODO: write logic for meta-categories e.g. maintanence categories [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/13]
    # [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/12]
    # see https://phabricator.wikimedia.org/T156612#3008806 on lacking description
    pass


def main():
    """Illustrate function-level docstring.
    
    Note that all docstrings begin with a one-line summary. The summary is
    written in the imperative mood ("do", "use", "find", "return", "render",
    etc) and ends with a period. The method signature is not, in any way,
    duplicated into the comments (that would be difficult to maintain).
    All subsequent paragraphs in a docstring are indented exactly the same as
    the summary line. The same applies to the closing quotation marks.
    """
    metadata_json = "SMVK-Cypern_2017-01_metadata.json"
    outpath = "./infofiles/"

    places = load_places_mapping()
    #print(places)

    metadata = load_json_metadata(metadata_json)
    for fotonr in metadata:
        outfile = open(outpath + fotonr + ".info", "w")
        full_infotext = ""
        infobox = generate_infobox_template(metadata[fotonr], places)
        full_infotext += infobox + "\n"

        #content_cats = generate_content_cats(metadata[fotonr])
        #infotext += content_cats + "\n"

        #meta_cats = generate_meta_cats(metadata[fotonr])
        #infotext += meta_cats

        #print(infotext + "\n--------------\n")
        #outfile.write(infotext)
        outfile.close()


if __name__ == '__main__':
    main()
