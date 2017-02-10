#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Create info files for batch SMVK-Cypern_2017-01
This is step 2 in the batchupload process for SMVK-Cypern_2017-01. Step 1. was to transform the Excel-metadata to
JSON-file ´SMVK-Cypern_2017-01_metadata.json´ and add new filenames, SMVK-MM-link and add Fotonummer as key..

Outputs <Fotonummer>.info files in a subdirectory ./infofiles/
"""

import os
import json


def load_json_metadata(infile):
    """Load metadata json blob created with ´metadata_to_json_and_fnamesmap.py´"""
    metadata = json.load(open(infile))

    return metadata

def generate_infobox_template(item):
    """Takes one item from metadata dictionary and constructs the infobox template.

    Return: item infobox as string
    """
    # TODO: write infobox logic based on https://phabricator.wikimedia.org/T156612
    pass


def generate_content_cats(item):
    """Takes one item from metadata dictionary and constructs the meta-categories.

        Return: meta-categories as string"""
    # TODO: write logic for content-categories
    pass

def generate_meta_cats(item):
    """Takes one item from metadata dictionary and constructs the meta-categories.

    Return: meta-categories as string"""
    # TODO: write logic for meta-categories e.g. maintanence categories
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
    outpath = "./infofiles"

    metadata = load_json_metadata(metadata_json)
    for fotonr in metadata:
        outfile = open(outpath + fotonr + ".info", "w")

        infotext = ""
        infobox = generate_infobox_template(metadata[fotonr])
        infotext += infobox + "\n"

        content_cats = generate_content_cats(metadata[fotonr])
        infotext += content_cats + "\n"

        meta_cats = generate_meta_cats(metadata[fotonr])
        infotext += meta_cats

        print(infotext + "\n--------------\n")
        #outfile.write(infotext)
        outfile.close()





if __name__ == '__main__':
    main()
