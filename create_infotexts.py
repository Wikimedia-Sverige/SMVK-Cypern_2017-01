#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""<HEADER OF YOUR MODULE DOCSTRING>.
Module-level docstrings appear as the first "statement" in a module. Remember,
that while strings are regular Python statements, comments are not, so an
inline comment may precede the module-level docstring.
After importing a module, you can access this special string object through the
``__doc__`` attribute; yes, it's actually available as a runtime attribute,
despite not being given an explicit name! The ``__doc__`` attribute is also
what is rendered when you call ``help()`` on a module, or really any other
object in Python.
You can also document a package using the module-level docstring in the
package's ``__init__.py`` file.
"""

import os
import batchupload.helpers as helpers

class ImageFile(object, original_fname, original_path):
    """One imagefile to be uploaded to Wikimedia Commons within this specific batchupload.

        Attributes:
            original_fname: A string representing the full original file name e.g. 2341D.34B.tif
            original_path: A string representing the original files relative path e.g. /Ext HD/
            commons_fname: A string representing the file name after adaptation to Wikimedia Commons conventions.

        """
    def __init__(self):
        self.original_fname = original_fname
        self.original_path = original_path
        self.commons_fname = None # Set after initiation by create_commons_filename()


    def create_commons_filename(self):
        """Does what is says """
        # TODO: use line 88 in https://github.com/lokal-profil/BatchUploadTools/blob/master/batchupload/helpers.py [Issue: https://github.com/mattiasostmar/SMVK-Cypern_2017-01/issues/8]
        # For Commons conventions see bit.ly/commons_fname_conventions


def main():
    """Illustrate function-level docstring.
    
    Note that all docstrings begin with a one-line summary. The summary is
    written in the imperative mood ("do", "use", "find", "return", "render",
    etc) and ends with a period. The method signature is not, in any way,
    duplicated into the comments (that would be difficult to maintain).
    All subsequent paragraphs in a docstring are indented exactly the same as
    the summary line. The same applies to the closing quotation marks.
    
    """


if __name__ == '__main__':
    main()
