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
import numpy as np

people_mapping_file = open("./people_mappings.json")
people_mapping = json.loads(people_mapping_file.read())


def load_places_mapping():
    """
    Read wikitable html into Pandas DataFrame, transform it and return a dictionary.
    
    :return: dictionary
    """
    kw_maps_url = "https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Cypern_places"
    places = pd.read_html(kw_maps_url, attrs={"class": "wikitable sortable"}, header=0)

    places_df = places[0]  # read_html returns a list of found tables, each of which as a dataframe
    places_df = places_df.set_index("Nyckelord")
    places_df.columns = ["freq", "commonscat", "wikidata"]

    places_df[places_df == "-"] = None

    places_dict = {}
    for index, row in places_df.iterrows():
        places_dict[index] = {}
        if row["commonscat"]:
            places_dict[index]["commonscat"] = row["commonscat"]
        places_dict[index]["wikidata"] = row["wikidata"]

    return places_dict


def load_keywords_mapping():
    """
    Read wikitable html into Pandas DataFrame, transform it and return a dictionary.
    
    :return: dictionary
    """
    kw_maps_url = "https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Cypern_keywords"
    keywords = pd.read_html(kw_maps_url, attrs={"class": "wikitable sortable"}, header=0)
    kw1 = keywords[0] # First is the actual column <Nyceklord>
    
    kw1 = kw1.set_index("Nyckelord")
    kw1 = kw1[["Commons category", "wikidata"]] # Remove col "fredquency" for boolean filtering to work
    
    kw1[kw1 == "-"] = None  # Pandas "boolean indexing" kung-fu to replace all "-" with None
    
    kw_dict = {}
    for index, row in kw1.iterrows():
        kw_dict[index] = {}
        if row["Commons category"]:
            kw_dict[index]["commonscat"] = row["Commons category"]
        kw_dict[index]["wikidata"] = row["wikidata"] # should always be present
    
    return kw_dict
    

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
    smvk_link = "{{{{SMVK-MM-link|{postnr}|{fotonr}}}}}".format(postnr=item["Postnummer"], fotonr=item["Fotonummer"])

    return smvk_link


def generate_infobox_template(item, img, places_mapping):
    """Takes one item from metadata dictionary and constructs the infobox template.
    :param item: one metadata row for one photo
    :param img: a CypernImage object
    :param places_mapping: dictionary containing Commons:Medelhavsmuseet/batchUploads/Cypern_places
    :returns: infobox for the item as a string
    """
    # run CypernImage processing
    img.process_depicted_people(item["Personnamn / avbildad"])
    img.process_depicted_place(item["Ort, foto"], places_mapping, item["Beskrivning"])
    img.enrich_description_field(item)

    infobox = ""
    infobox += "{{Photograph \n"

    # 22 characters from start of string to '='
    if not item["Personnamn / fotograf"] == "":
        infobox += "| photographer       =  {{Creator:John Lindros}}\n"
    else:
        infobox += "| photographer       = \n"

    infobox += "| title               =\n"

    infobox += "| description        = {{sv| "

    if item["Beskrivning"]:
        infobox += img.data["enriched_description"]
    else:
        infobox += "Svenska Cypernexpeditionen 1927–1931"  # Generates six cases only
        img.meta_cats.append("Media_contributed_by_SMVK_with_poor_description")

    infobox += "}}\n"
    infobox += "{{en|The Swedish Cyprus expedition 1927–1931}}"
    infobox += "\n"

    infobox += "| depicted people    = " + img.data["depicted_people"] + "\n"

    infobox += "| depicted place     = " + img.data["depicted_place"] + "\n"

    infobox += "| date               = "
    if not item["Fotodatum"] or item["Fotodatum"] == "1927-1931":
        infobox += "{{Between|1927|1931}}"
    else:
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
    outfile = open("./SMVK-Cypern_2017-02_wikiformat_data.json", "w")

    # Hack to printout a wikitable to copy-paste to WikiCommons
    # people = create_people_mapping_wikitable(people_mapping)

    places_mapping = load_places_mapping()
    keywords_mapping = load_keywords_mapping()
    # print(places_mapping)

    metadata = load_json_metadata(metadata_json)
    batch_info = {}
    for fotonr in metadata:
        desc = metadata[fotonr]["Beskrivning"]
        keyw = metadata[fotonr]["Nyckelord"]
        
        img = CypernImage()
        
        img.generate_list_of_stripped_keywords(keyw)
        img.create_commons_filename(metadata[fotonr])
        img.special_archaeological_exhibition_cat(desc)
        img.special_interior_of_tombs_cat(desc)

        img_info = {"filename": img.filename}

        infobox = generate_infobox_template(metadata[fotonr], img, places_mapping)
        img_info["info"] = infobox

        img.add_catch_all_category()
        img_info["cats"] = list(set(img.content_cats))

        img_info["meta_cats"] = list(set(img.meta_cats))

        batch_info[fotonr] = img_info


    outfile.write(json.dumps(batch_info, ensure_ascii=False, indent=4))
    outfile.close()


class CypernImage:
    """Process the information for a single image."""

    def __init__(self):
        """Instantiate a single instance of a processed image."""
        self.idno = None  # <Fotonummer> in metadata, used as unique identifier i filename
        self.content_cats = []  # content cateogories without 'Category:'-prefix
        self.meta_cats = []  # maintance categories without 'Category:'-prefix
        self.data = {}  # dictionary holding individual field values as wikitext
        self.filename = None  # without filename extension

        batch_cats = ["Swedish Cyprus Expedition",
                      "Media_contributed_by_SMVK_2017-02"]

        self.meta_cats.extend(batch_cats)


    def special_archaeological_exhibition_cat(self, description):
        """
        Special case fix to add content category in special cases from <Beskrivning>.
        
        See task: https://phabricator.wikimedia.org/T163317
        
        Populates self.content_cats
        
        :return: None
        """
        if "utställning" in description.lower():
            self.content_cats.append("Archaeological_exhibitions")

    def special_interior_of_tombs_cat(self, description):
        """
        Special case fix to add content category in special cases from <Beskrivning>.

        See task: https://phabricator.wikimedia.org/T163316

        Populates self.content_cats

        :return: None
        """
        if "interiör" in description.lower() and "grav" in description.lower():
            self.content_cats.append("Interiors_of_tombs")

    def create_commons_filename(self, item):
        """
        Transform original filename into Wikimedia commons style filename.

        See https://phabricator.wikimedia.org/T156612 for definition.
        Note: the returned filename does not include file extension e.g. '.tif'

        :param item: dictionary conatining metadata for one image
        :return: None (populates self.filename)
        """
        fname_desc = ""
        fname_desc += re.sub(" Svenska Cypernexpeditionen\.?", "", item["Beskrivning"])
        if not fname_desc.endswith("."):
            fname_desc += "."

        # Enrich with keywords
        keywords_to_append = []
        if self.data["keyword_list"]:
            for keyword in self.data["keyword_list"]:
                if keyword not in item["Beskrivning"]:
                    keywords_to_append.append(keyword)

        if keywords_to_append:
            fname_desc += " {}.".format(", ".join(keywords_to_append))

        # Enrich with regional data
        if not item["Ort, foto"] in item["Beskrivning"]:
            fname_desc += " {},".format(item["Ort, foto"])

        if not item["Region, foto"] in item["Beskrivning"]:
            fname_desc += " {},".format(item["Region, foto"])

        if not item["Land, foto"] in item["Beskrivning"]:
            fname_desc += " {},".format(item["Land, foto"])

        if fname_desc.endswith(","):
            fname_desc = "{}.".format(fname_desc.strip(","))

        # Ensure first descriptive part is not empty
        if not fname_desc.strip():
            fname_desc = "Svenska Cypernexpeditionen 1927–1931"

        fname_desc = fname_desc.replace("svenska cypernexpeditionen", "Svenska Cypernexpeditionen")

        self.filename = helpers.format_filename(fname_desc, "SMVK", item["Fotonummer"])

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
            self.meta_cats.append("Media_contributed_by_SMVK_with_faulty_depicted_person_values")
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
            name_as_wikitext = name_map["wikidata"]

        elif "commonscat" in name_map.keys():
            name_as_wikitext = "[[:Category:{commonscat}|{name}]]".format(
                commonscat=name_map["commonscat"],
                name=name_map["name"])

        else:
            name_as_wikitext = name_map["name"]

        if "commonscat" in name_map.keys():
            self.content_cats.append(name_map["commonscat"])

        return name_as_wikitext

    def process_depicted_place(self, place_string, places_mapping, desc_string):
        """
        Create wikiformat depicted place string from raw input data.
        
        Populates data["depicted_place"] and interacts with data["commonscat"] and data["meta_cats"].
        
        :param place_string: string value <Ort, foto> in metadata item.
        :param places_mapping: Dictionary containing Commons:Medelhavsmuseet/batchUploads/Cypern_places
        :param desc_string: string value <Beskrivning> in metadata item.
        :return: None (output stored in object attribute
        """
        place_as_wikitext = ""

        if place_string:

            if place_string in places_mapping:

                if place_string == "Stockholm":
                    # Mainly interiors from buildings gardens
                    self.meta_cats.append("Media_contributed_by_SMVK_without_mapped_place_value")
                    self.meta_cats.append("Media_contributed_by_SMVK_taken_somewhere_in_Stockholm")
                    place_as_wikitext = "Stockholm"

                elif place_string == "Macheras":
                    # No WP article, highly ambiguous. Might refer to "Machairas Monestary"
                    self.meta_cats.append("Media_contributed_by_SMVK_without_mapped_place_value")
                    self.meta_cats.append("Media_contributed_by_SMVK_possibly_depicting_Machairas_Monastary")
                    place_as_wikitext = "Macheras"

                elif places_mapping[place_string]["wikidata"]:
                    place_as_wikitext += "{{{{city|1={wikidata}}}}}".format(
                        wikidata=places_mapping[place_string]["wikidata"]
                        )

                else:
                    place_as_wikitext += place_string

                # Don't forget to add the commons categories, even though only wikidata is used in depicted people field
                if places_mapping[place_string].get('commonscat'):
                    self.content_cats.append(places_mapping[place_string]["commonscat"])

            else:
                place_as_wikitext += place_string


        else:
            place_matches = []
            for place in places_mapping:
                if place in desc_string:
                    if not "nicosiavägen" in desc_string.lower():
                        place_matches.append(place)

            if len(place_matches) == 1:
                place = place_matches[0]
                if places_mapping[place]["wikidata"]:
                    place_matches.append("{{{{city|1={wikidata}}}}}".format(
                        wikidata=places_mapping[place]["wikidata"]))
                else:
                    place_as_wikitext = place

                # Don't forget to add the commons categories if present.
                if places_mapping[place].get('commonscat'):
                    self.content_cats.append(places_mapping[place]["commonscat"])

            else:
                self.meta_cats.append("Media_contributed_by_SMVK_without_mapped_place_value")
                place_as_wikitext = place_string



        self.data["depicted_place"] = place_as_wikitext
        
    
    def process_keywords(self):
        """
        Add potential content categories from column <Nyckelord>.
        
        Populates self.content_cats
        
        :return: None
        """

    def generate_list_of_stripped_keywords(self, keyword_string):
        """
        Transform string of keywords from column <Nyckelord> to list of keywords.
        Remove "Svenska Cypernexpeditionen" and "fråga" if present.

        :param keyword_string: String from column <Nyckelord.
        :return: list of keywords.
        """
        keywords_list = keyword_string.split(", ")
        keywords_list_low = [kw.lower() for kw in keywords_list]
        if "Svenska Cypernexpeditionen" in keywords_list_low:
            keywords_list_low.remove("Svenska Cypernexpeditionen")

        if "fråga" in keywords_list_low:
            keywords_list_low.remove("fråga")


        self.data["keyword_list"] = keywords_list_low

    def enrich_description_field(self, item):
        """
        Try to add keywords and regional information to description.

        :param item: dictionary containing metadata for one image.
        :return: string representing altered description.
        """
        description = re.sub(" Svenska Cypernexpeditionen\.?", "", item["Beskrivning"])

        if not description.endswith("."):
            description += "."

        # Step 1 in enrichment process

        description += " Svenska Cypernexpeditionen 1927–1931. "

        # step 2 in enrichment process
        description += self.process_region_addition_to_description(
            item["Region, foto"],
            item["Land, foto"]
        )

        # step 3 in enrichment process
        if self.data["keyword_list"]:
            description += "<br>''Nyckelord:'' {}".format(', '.join(self.data["keyword_list"]))

        self.data["enriched_description"] = description

    @staticmethod
    def process_region_addition_to_description(region_str, country_str):
        """
        Add <Region, foto> to description string, except when it is already present, with some smartness.

        :param region_str: String with the field value from column <Region ,foto> in metadata.
        :param country_str: String with the field value from column <Land> in metadata. 
        :return: String with formatted region to add to description
        """
        region_addition = ""
        if region_str:
            region_addition += "<br>''Region:'' " + region_str
            if country_str:
                region_addition += ", " + country_str

        return region_addition

    def add_catch_all_category(self):
        """"
        Check if there are any content cats added and add generic content category to image.
        
        Populate self.content_cat with commons category, if present.
        """
        if not self.content_cats:
            self.meta_cats.append("Media_contributed_by_SMVK_needing additional_categorization")

if __name__ == '__main__':
    main()
