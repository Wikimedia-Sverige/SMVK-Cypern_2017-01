#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Turn Excel metadata from SMVK into JSON-file for further processing.

Input: Excel-file
Processing: strip whitespace etc
Output: JSON-file `cypern_metadata.json" containg dict in the current directory
"""
import pandas as pd
import argparse


def create_json_dict_file(metadata, outfile):
    # TODO: convert DataFrame to dict of rows
    fileobject = open(outfile, "w")
    fileobject.write(metadata.to_json())


def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text


cypern_converters = {"Fotonummer": strip, "Postnr": strip, "Nyckelord": strip, "Beskrivning": strip, "Land": strip,
                     "foto": strip,
                     "Region, foto": strip, "Ort, foto": strip, "Geograf namn, alternativ": strip, "Fotodatum": strip,
                     "Personnamn / fotograf": strip, "Personnamn / avbildad": strip, "Sökord": strip,
                     "Händelse / var närvarande vid": strip, "Länk": strip}


def main():
    """Read infile and output json-file and filenames mapping file."""
    try:
        metadata = pd.read_excel(args.infile, sheetname="Cypern", converters=cypern_converters)
        print("Loaded Excel-file into DataFrame OK: ")
        print(metadata.info())

        create_json_dict_file(metadata, args.outfile)

    except IOError as e:
        print("IOError: {}".format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", default="../excel-export.xls")
    parser.add_argument("--fnameFile", default="SMVK-Cypern_2017-01_filename_mappings.csv")
    parser.add_argument("--outfile", default="SMVK-Cypern_2017-01_metadata.json")
    args = parser.parse_args()
    main()
