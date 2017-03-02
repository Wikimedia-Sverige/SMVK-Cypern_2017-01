#! /usr/bin/env python
# -*- coding = utf-8 -*-

"""
    Script for taking care of batch-specific stuff.


    Try to incorporate the CRISP-DM standard in structure:
    https://www.the-modeling-agency.com/crisp-dm.pdf
    Data Preparation phase:
        3.1 Select data (Not OK to upload vs process batch item)
        3.2 Clean data (when transforming data to json blob)
        3.3. Construct data (new filename, description field etc)
        3.4. Integrate data (keyword mappings)
        3.5. Format data (cretae wikisyntax string)


    Information (attributes) about the batch e.g.:
        Batch name
        Metadata file location
        Media files location
        Keyword mappings


    Processes (methods) related to triggering stuff for the batch e.g.:
        Load metadata
        Load mappings
        Cleaning of metadata
        Transform cleaned metadata to json blob
        Process each batch item (using class CypernItem)
    """

import batchupload.helpers as helpers
import batchupload.common as common
import json
import os
import re
import batchupload.helpers as helpers

METADATA_PATH      = os.getcwd() # Avoid relative path and handle different home paths on Mac OS X and Linux,
METADATA_JSON_FILE = "SMVK-Cypern_2017-01_metadata.json"

def load_json_metadata(path, infile):
    """Load metadata json blob as dictionary for further processing.
    :infile: created with ´metadata_to_json_and_fnamesmap.py´
    :returns: dictionary with <Fotonummer> as keys e.g. `C03643` for image file `C03643.tif´
    """

    full_path = os.path.join(path, infile)
    metadata = json.load(open(full_path))

    print("metadata item C01427: {}".format(metadata["C01427"]))

    return metadata

class CypernItem(object):
    """
    Class for taking care of metadata-to-wikiCommons stuff per media file.

    Information (attributes) e.g.:
        New filename adopted to Wikimedia Commons conventions and guidelines
        Content categories (a.k.a. Commons categories)
        Maintanence categories (e.g. Media from SMVK-MM with faulty depicted people fields)
        Infotext i.e. Template:photograph with transformed values from metadata

    Processes (methods) e.g.:
        Create new filename
        Store new filename to metadata json blob
        Add content categor[y/-ies]
        Add maintanence categor[y/-ies]
        Populate photograph template

    """
    def __init__(self, metadata_dict):
        self.commons_fname = None
        self.maint_cats = None
        self.cont_cats = None
        self.metadata = metadata_dict

def main():
    metadata = load_json_metadata(METADATA_PATH, METADATA_JSON_FILE)

if __name__ == '__main__':
    main()

