"""
Overview
--------

Functions for extracting data from text files.

**Development Status:**
  **Last Modified:** December 22, 2010 by Charlie Sharpsteen
"""
#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from itertools import islice


#------------------------------------------------------------------------------
#  File Processing 
#------------------------------------------------------------------------------
# So. One place where Python really falls down compared to languages like R and
# Fortran is that it has no efficient syntax for saying things like "get me the
# next 10 floating point values from this file" that acts in a way similar to
# Fortran's `read` or R's `scan`.
#
# It turns out that there is a rather elegant and memory efficient way to do
# this in Python using generators---but it is hardly obvious to newcomers.
# These methods are adapted from the following answer on Stack Overflow:
#
#     http://stackoverflow.com/questions/4158265/
#       reading-very-large-file-where-format-is-newline-independent/
#       4158402#4158402
class FileScanner(object):
  def __init__(self, file_path):

    # The basic building block of this class is a generator that successively
    # yields items separated by ' ', '\t' or '\n'.
    def tokens(filename):
      with open(filename) as input:
        for line in input:
          for token in line.split():
            yield token

    self._token_stream = tokens(file_path)

  def scan(self, n, coerce = None):
    if coerce:
      return [coerce(token) for token in islice(self._token_stream, n)]
    else:
      return [token for token in islice(self._token_stream, n)]

  def skip(self, n):
    self.scan(n)
    return None

