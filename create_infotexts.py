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


def generate_infobox_template(item, places, img):
    """Takes one item from metadata dictionary and constructs the infobox template.
    :param item: one metadata row for one photo
    :param places:
    :param img: a CypernImage object
    :returns: infobox for the item as a string
    """
    # run CypernImage processing
    img.process_depicted_people(item["Personnamn / avbildad"])

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

    infobox += "| depicted people    = " + img.data["depicted_people"] + "\n"

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

        img = CypernImage()
        infobox = generate_infobox_template(metadata[fotonr], places, img)


        # print(infobox)
        full_infotext += infobox + "\n"

        # content_cats = generate_content_cats(metadata[fotonr])
        # full_infotext += content_cats + "\n" # content cats can also be added by depicted persons

        # meta_cats = generate_meta_cats(metadata[fotonr])
        # full_infotext += meta_cats

        print(full_infotext + "\n--------------\n")
        # outfile.write(infotext)
        outfile.close()


class CypernImage():
    """Process the information for a single image."""

    def __init__(self):
        """Instantiate a single instance of a processed image."""
        self.content_cats = []  # content cateogories wihtout 'Category:'-prefix
        self.meta_cats = []  # maintance categories without 'Category:'-prefix
        self.data = {}  # dictionary holding individual field values as wikitext

        batch_cats = ["Swedish Cyprus Expedition|Swedish Cyprus Expedition",
                      "Media_from_the_National_Museums_of_World_Culture",
                      "Media_contributed_by_SMVK_2017-02"]

        self.meta_cats.extend(batch_cats)


    def process_depicted_people(self, names_string):
        """
        Create depicted people wikitext from raw input data.

        Populates the data["depicted_people"] field in self and interacts with
        content_cats and meta_cats.
        
        If name interpratation fails, we still store the problematic string + maintanence category.

        :param names_string: string representing one or more names.
        """
        try:
            names = CypernImage.isolate_name(names_string)
        except ValueError:
            self.meta_cats.append("Media_contributed_by_SMVK_2017-02_with_faulty_depicted_person_values")
            self.data["depicted_people"] = names_string
            return

        wikitext_names = []
        for name in names:
            wikitext_names.append(self.select_best_mapping_for_depicted_person(name))

        self.data["depicted_people"] = "/".join(wikitext_names)



    @staticmethod
    def isolate_name(names_string):
        """
        Try isolating names and flipping names.

        Expected input is a string with 'last1, first1, last2, first2...'

        :param names_string: string representing depicted people
        :return: list of flipped names.
        :raises: ValueError if uneven number of names
        """
        if not names_string:
            return []

        if len(names_string.split(", ")) % 2 != 0:
            raise ValueError("Uneven number of names.")

        # Pairwise group name parts
        words = names_string.split(", ")
        span = 2
        grouped_names = [", ".join(words[i:i + span]) for i in range(0, len(words), span)]

        names = []
        for name_pair in grouped_names:
            flipped_name = helpers.flip_name(name_pair)
            names.append(flipped_name)
        return names

    def select_best_mapping_for_depicted_person(self, flipped_name):
        """
        Lookup available mappings for a string respresenting a name and return best choice.
        
        people_mapping is complete by design.
        
        The priority order is wikidata item < commons category < the name only.
        :flipped_name: string representing full name turned around from
            e.g. "surname, given name" -> "given name surname"
            note that give_name is normally one word e.g. "Erfraim"
        :return:  string representing the selcted mapping value
        """
        name_map = people_mapping[flipped_name]
        name_as_wikitext = ""
        if "wikidata" in name_map.keys():
            name_as_wikitext = "[[:d:{wd_item}|{name}]]".format(
                wd_item=name_map["wikidata"],
                name=name_map["name"])

        elif "commonscat" in name_map.keys():
            name_as_wikitext = "[[Category:{commonscat}|{name}]]".format(
                commonscat=name_map["commonscat"],
                name=name_map["name"])

        else:
            name_as_wikitext = name_map["name"]

        if "commonscat" in name_map.keys():
            self.content_cats.append(name_map["commonscat"])

        return name_as_wikitext


if __name__ == '__main__':
    main()