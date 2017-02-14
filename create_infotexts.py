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

def load_places_mapping():
    """Reads wikitable html and returns a dictionary"""
    kw_maps_url = "https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Cypern_places"
    places = pd.read_html(kw_maps_url, attrs={"class": "wikitable sortable"}, header=0)

    places_df = places[0] # read_html returns a list of found tables, each of which as a dataframe
    return places_df.to_dict()

def load_json_metadata(infile):
    """Load metadata json blob created with ´metadata_to_json_and_fnamesmap.py´"""
    metadata = json.load(open(infile))

    return metadata

def generate_infobox_template(item):
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

    if not item["Personnamn / avbildad"] == "":
        infobox += "| depicted people    = " + item["Personnamn / avbildad"]
    else:
        infobox += "| depicted people    = "


#  |depicted place     = {{city|<Places mapping>}}
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
    #print(infobox)

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
    print(places)

    metadata = load_json_metadata(metadata_json)
    for fotonr in metadata:
        outfile = open(outpath + fotonr + ".info", "w")
        full_infotext = ""
        infobox = generate_infobox_template(metadata[fotonr])
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
