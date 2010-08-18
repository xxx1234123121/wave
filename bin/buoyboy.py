#!/usr/bin/env python
"""
-------------------------------------------------------------------
This script retrieves buoy data from the NDBC.

Version:       0.1.0
Author:        Charlie Sharpsteen <source@sharpsteen.net>
Last Modified: August 17, 2010 by Charlie Sharpsteen
-------------------------------------------------------------------
"""

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


import datetime

from wavecon.NDBC import fetchBuoyRecords


"""
-------------------------------------------------------------------
   Utility Functions
-------------------------------------------------------------------
"""
def ISO_datestring( aString ):
  """Takes a string in 'unambiguous format' and returns a datetime object.

  Here, 'unambiguous format' is arbitrarily declared to be a subset of the
  ISO 8601 format:

     %Y-%m-%dT%H:%M:%S

  """

  return datetime.datetime.strptime( aString, '%Y-%m-%dT%H:%M:%S' )


"""
-------------------------------------------------------------------
   Main Script and Supporting Functions
-------------------------------------------------------------------
"""
def processArgs():
  """Processes command-line arguments and returns a loaded ArgumentParser."""
  import argparse

  parser = argparse.ArgumentParser( description = 'BuoyBoy: A buoy data fetcher.' )

  # Flag arguments- these are optional and distinguished by -something
  parser.add_argument( '-v', action = 'store_true', dest = 'be_verbose',
                       help = 'Should BuoyBoy pretend he is called ChattyCathy?' )

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
  parser.add_argument( 'buoyNum', metavar = 'Buoy#', type = int,
                       help = 'The number of the NDBC buoy for which you wish to fetch data.' )

  parser.add_argument( 'startTime', metavar = 'StartTime', type = ISO_datestring,
                        help = '''The starting time for data you wish to download. Must be in the 
                        following format "year-month-dayThour:minute:second"''' )
  parser.add_argument( 'stopTime', metavar = 'StopTime', type = ISO_datestring,
                        help = '''The end of the time range for which data is to be downloaded. 
                        Uses the same format as described above.''' ) 

  parser.add_argument( 'windFile', nargs = '?', action = 'store', default = '',
                       help = '''If --format was set to json (the default),
                       specifies the name of the output file to which downloaded
                       wind data should be dumped as JSON records.  If left
                       blank, records will be written to the screen.''' )

  parser.add_argument( 'waveFile', nargs = '?', action = 'store', default = '',
                       help = '''Controls output of downloaded wave data.  See
                       the windFile argument for details.''' )

  args = parser.parse_args()
  return args


if __name__ == '__main__':
  """ 
  This is the actual script part.  Building a script file this way allows it to
  be used as both a command line tool and a python library.  Then other Python
  scripts can import functions from this one without running the script.
  """
  
  args = processArgs()

  windRecords, waveRecords = fetchBuoyRecords( args.buoyNum,
    args.startTime, args.stopTime,
    'meteorological'
  )

  if args.output_format == 'json':
    from wavecon.NDBC.JSON import writeJSON

    if args.windFile:
      file = open( args.windFile, 'w' )
      writeJSON( windRecords, file )
      file.close()
    else:
      file = sys.stdout
      writeJSON( windRecords, file )

    if args.waveFile:
      file = open( args.waveFile, 'w' )
      writeJSON( waveRecords, file )
      file.close()
    else:
      file = sys.stdout
      writeJSON( waveRecords, file )

  elif args.output_format == "matlab":
    from wavecon.NDBC.matlab import writeMatFile

    if not args.windFile:
      args.windFile = "NDBCwindData.mat"
    writeMatFile( windRecords, 'NDBCwind', args.windFile )

    if not args.waveFile:
      args.waveFile = "NDBCwaveData.mat"
    writeMatFile( waveRecords, 'NDBCwave', args.waveFile )
    
  else:
    raise NotImplementedError("Database support has not been finalized yet.")
