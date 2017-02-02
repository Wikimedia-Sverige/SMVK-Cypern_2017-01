#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Turn Excel metadata from SMVK into JSON-file for further processing.

Input: Excel-file
Processing: strip whitespace etc
Output: JSON-file `cypern_metadata.json" containg dict in the current directory
"""
import pandas as pd
import argparse

def main():
    """Illustrate function-level docstring.
    
    Note that all docstrings begin with a one-line summary. The summary is
    written in the imperative mood ("do", "use", "find", "return", "render",
    etc) and ends with a period. The method signature is not, in any way,
    duplicated into the comments (that would be difficult to maintain).
    All subsequent paragraphs in a docstring are indented exactly the same as
    the summary line. The same applies to the closing quotation marks.
    
    """
    try:
        metadata = pd.read_excel(args.infile)
    except IOError as e:
        print("IOError: {}".format(e))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile",default="../excel-export.xls")
    parser.add_argument("--fname-file",default="SMVK-Cypern_2017-01_filename_mappings.csv")
    parser.add_argument("-outfile", default="SMVK-Cypern_2017-01_metadata.json")
    args = parser.parse_args()
    main()