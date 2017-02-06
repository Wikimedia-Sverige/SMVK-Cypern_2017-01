#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Turn Excel metadata from SMVK into JSON-file for further processing.

Input: Excel-file
Processing: strip whitespace etc
Output: JSON-file `cypern_metadata.json" containg dict in the current directory
"""
import pandas as pd
import argparse
import json
import os

def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text


cypern_converters = {"Fotonummer": strip, "Postnr.": strip, "Nyckelord": strip, "Beskrivning": strip, "Land, foto": strip,
                     "Region, foto": strip, "Ort, foto": strip, "Geograf namn, alternativ": strip,
                     "Fotodatum": strip, "Personnamn / fotograf": strip, "Personnamn / avbildad": strip, "Sökord": strip,
                     "Händelse / var närvarande vid": strip, "Länk": strip}

def populate_new_dict_with_metadata(metadata, new_dict):
    for fotonr in metadata.Fotonummer:
        new_dict[fotonr] = {}

    # ensure empty fields are ""
    metadata.fillna("", inplace=True)

    for index, row in metadata.iterrows():
        #print(row)
        #break
        new_dict[row["Fotonummer"]]["Postnummer"] = row["Postnr."]
        new_dict[row["Fotonummer"]]["Nyckelord"] = row["Nyckelord"]
        new_dict[row["Fotonummer"]]["Beskrivning"] = row["Beskrivning"]
        new_dict[row["Fotonummer"]]["Land, foto"] = row["Land, foto"]
        new_dict[row["Fotonummer"]]["Region, foto"] = row["Region, foto"]
        new_dict[row["Fotonummer"]]["Ort, foto"] = row["Ort, foto"]
        new_dict[row["Fotonummer"]]["Geograf namn, alternativ"] = row["Geograf namn, alternativ"]
        new_dict[row["Fotonummer"]]["Fotodatum"] = row["Fotodatum"]
        new_dict[row["Fotonummer"]]["Personnamn / fotograf"] = row["Personnamn / fotograf"]
        new_dict[row["Fotonummer"]]["Personnamn / avbildad"] = row["Personnamn / avbildad"]
        new_dict[row["Fotonummer"]]["Sökord"] = row["Sökord"]
        new_dict[row["Fotonummer"]]["Händelse / var närvarande vid"] = row["Händelse / var närvarande vid"]
        new_dict[row["Fotonummer"]]["Länk"] = row["Länk"]

    return new_dict

def check_image_dir(image_dir):
    """Ensures that images are all in one directory and has extension .tif"""

    for root, dirs, files in os.walk(image_dir):
        if len(dirs) > 0:
            print("{} subdirectories found in path 'image_dir': {}".format(len(dirs), dirs))
            print("Expected no subdirectories - exiting.")
        else:
            for file in files:
                ext = os.path.splitext(file)
                if ext != ".tif":
                    print("Unexpected extension: {} for file {}".format(ext, file))
                else:
                    print(ext)
    print("Succesfully finished checking that image files looks like expected.")

def add_commons_filenames_to_dict(metadata, new_dict):
    """Creates commons filename according to https://phabricator.wikimedia.org/T156612 and ouputs to new_dict"""

    for index, row in metadata.iterrows():
        commons_name = ""
        commons_name += row["Beskrivning"]
        commons_name += "_-_SMVK-MM-Cypern_-_"
        commons_name += row["Fotonummer"]
        commons_name += ".tif"

        new_dict[row["Fotonummer"]]["commons_fname"] = commons_name

        print("Fotonummer: {} - Commons name: {}".format(metadata["Fotonummer"], commons_name))
        return new_dict

def add_smvk_mm_link_to_dict(metadata, new_dict):

    # TODO: Add SMVK-MM-Link, see https://sv.wikipedia.org/wiki/Mall:SMVK-MM-l%C3%A4nk [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/5]
    for index, row in metadata.iterrows():
        url = row["Länk"]
        url_str = url.to_string()
        obj_id = url_str.rpartition("/")[2]
        print(obj_id)

def create_linked_filenamesmapping_wikitable_file(new_dict):
    pass


def save_metadata_json_blob(new_dict):
    pass


def main(args):
    """Read infile and output json-file and filenames mapping file."""

    new_dict = {}

    try:
        metadata = pd.read_excel(args.metadata, sheetname="Cypern", converters=cypern_converters)
        print("Loaded Excel-file into DataFrame OK: ")
        print(metadata.info())

        check_image_dir(args.image_dir)

        populated_dict = populate_new_dict_with_metadata(metadata, new_dict)
        print("populated_dict: {}".format(populated_dict))

        #dict_with_commons_filenames = add_commons_filenames_to_dict(metadata, new_dict)
        #print(dict_with_commons_filenames)
        #dict_with_smvk_mm_link = add_smvk_mm_link_to_dict(metadata, dict_with_commons_filenames)

        #create_linked_filenamesmapping_wikitable_file(dict_with_smvk_mm_link)

        #save_metadata_json_blob(dict_with_smvk_mm_link, args.json_out)

    except IOError as e:
        print("IOError: {}".format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", default="../excel-export.xls")
    parser.add_argument("--image_dir", default="/media/mos/My Passport/Wikimedia/Cypern")
    parser.add_argument("--fname_out", default="SMVK-Cypern_2017-01_filename_mappings.csv")
    parser.add_argument("--json_out", default="SMVK-Cypern_2017-01_metadata.json")
    arguments = parser.parse_args()
    main(arguments)
