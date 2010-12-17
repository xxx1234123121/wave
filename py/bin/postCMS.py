#!/usr/bin/env python

#------------------------------------------------------------------
# This script post-processes CMS output.
# 
# Version:       0.1.0
# Author:        Charlie Sharpsteen <source@sharpsteen.net>
# Last Modified: October 18, 2010 by Charlie Sharpsteen
#------------------------------------------------------------------

import sys
if sys.version_info < (2, 7):
  import warnings
  warnings.warn( '''This script was develped on python 2.7, 
                    there may be bugs with earlier versions!''' )

# Make sure the WaveConnect py/lib folder is on the search path so
# modules can be retrieved.
from os import path
scriptLocation = path.dirname(path.abspath( __file__ ))
waveLibs = path.abspath(path.join( scriptLocation, '..', 'lib' ))
sys.path.insert( 0, waveLibs )

from wavecon.CMS import load_run_metadata

#------------------------------------------------------------------
#  Utility Functions
#------------------------------------------------------------------
def ISO_datestring( aString ):
  """Takes a string in 'unambiguous format' and returns a datetime object.

  Here, 'unambiguous format' is arbitrarily declared to be a subset of the
  ISO 8601 format:

     %Y-%m-%dT%H:%M:%S

  """

  return datetime.datetime.strptime( aString, '%Y-%m-%dT%H:%M:%S' )


def check_cmcards( aString ):

  cmcardsPath = path.abspath( aString )

  if path.isfile( cmcardsPath ):
    return cmcardsPath
  
  else:
    raise IOError(
      '''The CMS cmcards file specified, {0}, could not be found.'''.format(cmcardsPath)
    )


#------------------------------------------------------------------
#  Main Script and Supporting Functions
#------------------------------------------------------------------
def processArgs():
  """Processes command-line arguments and returns a loaded ArgumentParser."""
  import argparse

  parser = argparse.ArgumentParser( description = 'postCMS: CMS model post processor' )

  # Flag arguments- these are optional and distinguished by -something
  parser.add_argument( '-v', action = 'store_true', dest = 'be_verbose',
                       help = '''Should postCMS spare no bytes in order to produce
                       as much output as possible?''' )

  parser.add_argument( '--format', action = 'store', dest ='output_format',
                       choices = ['database', 'json','matlab'],
                       default = 'json',
                       help = '''The format of output- may be 'database', 'json'
                       or 'matlab'.  If database is selected, downloaded data
                       will be serialized to a relational database.  If json
                       output is selected, downloaded data will be serialized to
                       JSON format and either dumped to the screen or written to
                       a file depending on the values of windFile and
                       waveFile.  When matlab is selected, the SciPy library
                       will be used to create a mat file, again using the names
                       passed by windFile and waveFile.'''
                     )

  # Positional arguments- these are not identified by a flag.  Rather their
  # meaning is inferred from their position in the command line.
  parser.add_argument( 'cmcards', metavar = 'cmcards file', type = check_cmcards,
                       help = '''The path to the cmcards file of the run you
                       wish to post-process.''' )

  args = parser.parse_args()
  return args


if __name__ == '__main__':
  """ 
  This is the actual script part.  Building a script file this way allows it to
  be used as both a command line tool and a python library.  Then other Python
  scripts can import functions from this one without running the script.
  """
  
  args = processArgs()

  cms_data = load_run_metadata( args.cmcards )

  from pprint import pprint
  pprint(cms_data)

  if args.output_format == 'json':
    print 'json\n'
  elif args.output_format == "matlab":
    print 'matlab\n'
  elif args.output_format == "database":
    print 'database\n'
  else:
    raise NotImplementedError('''The output format you specified, {0}, does not
    exist.  In fact, you should not have been allowed to specify it.  In either
    case, there is no implementation.'''.format( args.output_format ))
