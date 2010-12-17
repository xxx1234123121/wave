"""
Overview
--------

This module provides routines for performing common input/output operations.
This allows tools to provide a consistant set of options.

Currently, support for the following output is provided:

- JSON files
- MATLAB files

**Development Status:**
  **Last Modified:** December 16, 2010 by Charlie Sharpsteen

"""
from .JSON import writeJSON, clobber
from .matlab import writeMatFile
