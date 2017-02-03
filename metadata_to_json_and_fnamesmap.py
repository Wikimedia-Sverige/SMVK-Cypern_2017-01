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


def create_new_filenames(df, image_dir):
    """Inputs Pandas DataFrame and returns a dict.

    :returns {"old_name":"new_name"}
    """
    fname_dict = {}
    # TODO: add logic to create new filenames after review of https://phabricator.wikimedia.org/T156612 [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/2]

    return fname_dict


def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text


cypern_converters = {"Fotonummer": strip, "Postnr": strip, "Nyckelord": strip, "Beskrivning": strip, "Land": strip,
                     "foto": strip, "Region, foto": strip, "Ort, foto": strip, "Geograf namn, alternativ": strip,
                     "Fotodatum": strip, "Personnamn / fotograf": strip, "Personnamn / avbildad": strip, "Sökord": strip,
                     "Händelse / var närvarande vid": strip, "Länk": strip}


def create_filenames_mapping_file(new_old_filenames_dict, metadata, fname_out, image_dir):
    """Locates the external HD depending on platform and scans files and maps to json-file names."""
    # TODO: Add function to generate Commons names and add to json_file. [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/3]

    assert isinstance(new_old_filenames_dict, dict)

    fileobject = open(fname_out, "w")

    data = {}

    for index, row in metadata.iterrows():
        row_dict = row.to_dict()
        row_dict_as_string = str(row_dict)

        for root, dirs, files in os.walk(image_dir):
            del row_dict["Fotonummer"]
            if len(dirs) > 0:
                print("{} subdirectories found in path 'image_dir': {}".format(len(dirs), dirs))
                data[row["Fotonummer"]] = row_dict_as_string
                print("Expected no subdirectories - exiting.")
            else:
                print("len(dirs) >0!")
                for file in files:
                    ext = os.path.splitext(file)
                    if ext != ".tif":
                        print("Unexpected extension: {} for file {}".format(ext, file))
                    else:
                        print(ext)

    fileobject.write(json.dumps(data, ensure_ascii=False, indent=4))
    print("Succesfully created filenames mapping file {}!".format(fileobject.name))


def create_metadata_json_blob(metadata, new_old_filenames_dict, json_out):
    """Adds new filenames to metadata and stores it in a file as json-dictionary"""

    # TODO: Add SMVK-MM-Link

    fileobject = open(json_out, "w")

    # TODO: create metadata dictionary, del dict["Fotonummer"], conc metadata with mappings_dict [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/4]
    conc_metadata = None

    fileobject.write(conc_metadata)


def main(args):
    """Read infile and output json-file and filenames mapping file."""
    try:
        metadata = pd.read_excel(args.metadata, sheetname="Cypern", converters=cypern_converters)
        print("Loaded Excel-file into DataFrame OK: ")
        print(metadata.info())

        new_old_filenames_dict = create_new_filenames(metadata, args.image_dir)
        
        create_filenames_mapping_file(new_old_filenames_dict, metadata, args.fname_out, args.image_dir)
        
        create_metadata_json_blob(metadata, new_old_filenames_dict, args.json_out)

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
