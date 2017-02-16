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
		"commons": "[[Category:John Lindros|John Lindros]]",
		"wikidata": "[[:d:Q5957823|John Lindros]]"
	},
	"Lazaros Kristos": {
		"commons": "Lazaros Kristos"
	},
	"Alfred Westholm": {
		"commons": "[[Category:Alfred Westholm|Alfred Westholm]]",
		"wikidata": "[[:d:Q6238028|Alfred Westholm]]"
	},
	"Erik Sjökvist": {
		"commons": "[[Category:Erik Sjöqvist|Erik Sjöqvist]]",
		"wikidata": "[[:d:Q5388837|Erik Sjöqvist]]"
	},
	"Erik Sjöqvist": {
		"commons": "[[Category:Erik Sjöqvist|Erik Sjöqvist]]",
		"wikidata": "[[:d:Q5388837|Erik Sjöqvist]]"
	},
	"Einar Gjerstad": {
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
		"commons": "[[Category:Martin Gjerstad|Martin Gjerstad]]",
		"wikidata": "[[d:Q16632979|Martin Gjerstad]]"
	},
	"Knut Thyberg": {
		"commons": "[[Category:Knut Thyberg|Knut Thyberg]]",
		"wikidata": "[[:d:Q16633505|Knut Thyberg]]"
	},
	"Rosa Lindros": {
		"name":"Rosa Lindros"
	},
	"Ernst Kjellberg": {
		"commons": "[[Category:Ernst Kjellberg|Ernst Kjellberg]]",
		"wikidata": "[[:d:Q5911946|Ernst Kjellberg]]"
	},
	"Bror Millberg": {
		"commons": "Bror Millberg"
	}
}"""

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
    pass

def generate_infobox_template(item, places):
    """Takes one item from metadata dictionary and constructs the infobox template.

    Return: item infobox as string
    """
    # TODO: write infobox logic based on https://phabricator.wikimedia.org/T156612 [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/11]
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

    def depicted_people_mapping(people_mapping_string, name_string_or_list):

        people_mapping = json.loads(people_mapping_string)

        if isinstance(name_string_or_list, list):
            out_string = ""
            for name in name_string_or_list:
                out_string += str(people_mapping[name]) + "/"
            return out_string.rstrip("/")
        else: # pre-supposes isinstance(name_string_or_list, basetring) == True
            return people_mapping[name_string_or_list]

    if not item["Personnamn / avbildad"] == "":
        if len(item["Personnamn / avbildad"].split(", ")) <= 2:
            flipped_name = helpers.flip_name(item["Personnamn / avbildad"])
            mapped_name = depicted_people_mapping(people_mapping_string, flipped_name)
            infobox += "| depicted people    = " + str(mapped_name)
        else:
            #print("Bökig | depicted person: {}".format(item["Personnamn / avbildad"]))
            words = item["Personnamn / avbildad"].split(", ")
            if len(words) % 2 == 0:
                span = 2
                list_of_names = [", ".join(words[i:i + span]) for i in range(0, len(words), span)]
                flipped_names_list = helpers.flip_names(list_of_names)
                #print(flipped_names_list)
                mapped_people = depicted_people_mapping(people_mapping_string, flipped_names_list)
                infobox += "| depicted people    = " + mapped_people
            else:
                print("Error: not even number of names in depicted people: {}".format(item["Personnamn / avbildad"]))
    else:
        infobox += "| depicted people    = "
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
