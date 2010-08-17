#!/usr/bin/env python
"""
-------------------------------------------------------------------
This script retrieves buoy data from the NDBC.

Version:       0.1.0
Author:        Charlie Sharpsteen <source@sharpsteen.net>
Last Modified: July 23, 2010 by Charlie Sharpsteen
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

import json


from wavecon.NDBC import downloader


"""
-------------------------------------------------------------------
   Utility Functions
-------------------------------------------------------------------
"""
def ISO_datestring( aString ):
  """Takes a string in 'unambiguous format' and returns a datetime object.

  Here, 'unambiguous format' is arbitrarily declared to be that used by R if
  no format specification is provided:

     %m/%d/%Y %H:%M:%S

  """

  return datetime.datetime.strptime( aString, '%m/%d/%Y %H:%M:%S' )

def JSON_datestring( aObject ):
  if isinstance( aObject, datetime.datetime ):
    return aObject.isoformat()
  else:
    return None


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
                       choices = ['database', 'json'], default = 'json',
                       help = '''The format of output- may be 'database' or
                       'json'.  If database is selected, downloaded data will be
                       serialized to a relational database.  If json output is
                       selected, downloaded data will be serialized to JSON
                       format and either dumped to the screen or written to a
                       file depending on the values of windFile and waveFile.'''
                     )

  # Positional arguments- these are not identified by a flag.  Rather their meaning is
  # inferred from their position in the command line.
  parser.add_argument( 'buoyNum', metavar = 'Buoy#', type = int,
                       choices = [46022, 46212, 46244],
                       help = 'The number of the NDBC buoy for which you wish to fetch data.' )

  parser.add_argument( 'startTime', metavar = 'StartTime', type = ISO_datestring,
                        help = '''The starting time for data you wish to download. Must be in the 
                        following format "month/day/year hour:minute:second"''' )
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
  This is the actual script part.  Building a script file this way allows it to be used
  as both a command line tool and a python library.  Then other Python scripts can import
  functions from this one without running the script.
  """
  
  args = processArgs()

  windRecords, waveRecords = downloader.fetchBuoyRecords( args.buoyNum, args.startTime, args.stopTime, 'meteorological' )

  if args.output_format == 'json':

    if args.windFile:
      file = open( windFile, 'w' )
    else:
      file = sys.stdout

    file.write(json.dumps(
      windRecords,
      indent = 2,
      default = JSON_datestring
    ))

    if args.windFile: file.close()

    if args.waveFile:
      file = open( waveFile, 'w' )
    else:
      file = sys.stdout

    file.write(json.dumps(
      waveRecords,
      indent = 2,
      default = JSON_datestring
    ))
    
  else:
    print 'database commit- to be added.'
    #NDBC.commitToDB( windRecords )
    #NDBC.commitToDB( waveRecords )


  #print json.dumps( windData, indent = 4, default = checkForDate )

  #print "\n\n Stats: %i objects for %i days worth of data.\n" % ( len(windData), (args.stopTime - args.startTime).days )
