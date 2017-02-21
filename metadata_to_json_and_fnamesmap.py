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
import datetime
import batchupload
import batchupload.helpers as helpers

def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text


cypern_converters = {"Fotonummer": strip, "Postnr.": strip, "Nyckelord": strip, "Beskrivning": strip, "Land, foto": strip,
                     "Region, foto": strip, "Ort, foto": strip, "Geograf namn, alternativ": strip,
                     "Fotodatum": strip, "Personnamn / fotograf": strip, "Personnamn / avbildad": strip, "Sökord": strip,
                     "Händelse / var närvarande vid": strip, "Länk": strip}


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


def populate_new_dict_with_metadata(metadata, new_dict):
    for fotonr in metadata.Fotonummer:
        new_dict[fotonr] = {}

    # ensure empty fields are ""
    metadata.fillna("", inplace=True)

    for index, row in metadata.iterrows():
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


def add_commons_filenames_to_dict(metadata, populated_dict):
    """Creates commons filename according to https://phabricator.wikimedia.org/T156612 and ouputs to new_dict
    :type populated_dict: dictionary
    """
    for index, row in metadata.iterrows():
        if pd.notnull(row.Beskrivning):
            cleaned_fname = helpers.format_filename(row["Beskrivning"], "SMVK-MM-Cypern", row["Fotonummer"])
            #print("Fname using BatchUploadTools: {}".format(cleaned_fname))
        else:
            # TODO: fix alternative description according to https://phabricator.wikimedia.org/T156612#3008806 [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/9]
            beskr = "Svenska Cypernexpeditionen 1927-1931"
            cleaned_fname = helpers.format_filename(beskr, "SMVK-MM-Cypern", row["Fotonummer"])


        populated_dict[row["Fotonummer"]]["commons_fname"] = cleaned_fname + ".tif"

    return populated_dict


def create_linked_filenamesmapping_file(metadata_dict):
    """Inputs dictionary and outputs CSV-file with old vs new filenames.
    original|commons
    :output fileobject "
    """

    outfile = open("./SMVK-Cypern_filenames_mappings.csv","w")
    for fotonr in metadata_dict:
        old_name = fotonr + ".tif"
        new_name = metadata_dict[fotonr]["commons_fname"]
        outfile.write(old_name + "|" + new_name + "\n")

    outfile.close()

    print("Successfully wrote file './SMVK-Cypern_filenames_mappings.csv'")


def save_metadata_json_blob(metadata_dict, json_out):
    """Save json dictionary to file.
    :output fileobjet "./SMVK-Cypern_2017-01_metadata.json"
    """
    outfile = open(json_out,"w")
    outfile.write(json.dumps(metadata_dict, ensure_ascii=False, indent=4, cls=datetimeEncoder))
    outfile.close()

    print("Successfully wrote file {}".format(json_out))

class datetimeEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, datetime.datetime):
             return obj.isoformat()
         # Let the base class default method raise the TypeError
         return json.JSONEncoder.default(self, obj)


def main(args):
    """Read infile and output json-file and filenames mapping file."""

    new_dict = {}

    try:
        metadata = pd.read_excel(args.metadata, sheetname="Cypern", converters=cypern_converters)
        print("Loaded Excel-file into DataFrame OK: ")
        print(metadata.info())

        check_image_dir(args.image_dir)

        populated_dict = populate_new_dict_with_metadata(metadata, new_dict)
        #print("populated_dict: {}".format(populated_dict))

        dict_with_smvk_mm_link =
        print(dict_with_smvk_mm_link)

        create_linked_filenamesmapping_file(dict_with_smvk_mm_link)

        save_metadata_json_blob(dict_with_smvk_mm_link, args.json_out)

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
