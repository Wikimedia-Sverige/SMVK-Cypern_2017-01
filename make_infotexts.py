#! /usr/bin/env python
# -*- coding = utf-8 -*-

from batchupload.make_info import MakeBaseInfo
import json
import re
import pandas as pd
import batchupload.helpers as helpers


class CypernBatch(MakeBaseInfo)
    """
    Class for taking care of batch-specific stuff.


    Try to incorporate the CRISP-DM standard in structure:
    https://www.the-modeling-agency.com/crisp-dm.pdf
    Data Preparation phase:
        3.1 Select data (Not OK to upload vs process batch item)
        3.2 Clean data (when transforming data to json blob)


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
    def __init__(self, PEOPLE_MAPPING, ):

class CypernItem(object)
    """
    Class for taking care of metadata-to-wikiCommons stuff per media file.

    Try to incorporate the CRISP-DM standard in structure:
    https://www.the-modeling-agency.com/crisp-dm.pdf
    3.1 Data Preparation:
        3.3. Construct data (new filename, description field etc)
        3.4. Integrate data (keyword mappings)
        3.5. Format data (cretae wikisyntax string)


    Information (attributes) e.g.:
        New filename adopted to Wikimedia Commons conventions and guidelines
        Content categories (a.k.a. Commons categories)
        Maintanence categories (e.g. Media from SMVK-MM with faulty depicted people fields)
        Infotext i.e. Template:photograph with transformed values from metadata

    Processed (methods) e.g.:
        Create new filename
        Store new filename to metadata json blob
        Add content categor[y/-ies]
        Add maintanence categor[y/-ies]
        Populate photograph template

    """