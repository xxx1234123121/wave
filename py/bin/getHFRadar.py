#!/usr/bin/env python
"""
-------------------------------------------------------------------
This script retrieves HF Radar derived surface current data from 
sdf.ndbc.noaa.gov.

Version:       0.1.0
Author:        Colin Sheppard (colin@humboldt.edu), code template
               by Charles Sharpsteen (source@sharpsteen.net)
Last Modified: July 26, 2010 by Colin Sheppard
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
from wavecon import DBman
from wavecon import HFRadar
from wavecon.config import DBconfig

"""
-------------------------------------------------------------------
   Utility Functions
-------------------------------------------------------------------
"""
def ISO_datestring( aString ):
  """Takes a string in 'unambiguous format' and returns a datetime object.

  Here, 'unambiguous format' is arbitrarily declared to be that used by R if
  no format specification is provided:

     %Y-%m-%d %H:%M:%S

  """
  return datetime.datetime.strptime( aString, '%Y-%m-%d %H:%M:%S' )

"""
-------------------------------------------------------------------
   Main Script and Supporting Functions
   example usage:  python hfradar.py -v 38 42 -128 -123 "2010-07-25 00:00:00" "2010-07-26 00:00:00" 6km
-------------------------------------------------------------------
"""
def processArgs():
  """Processes command-line arguments and returns a loaded ArgumentParser."""
  import argparse

  parser = argparse.ArgumentParser( description = 'BuoyBoy: A buoy data fetcher.' )

  # Flag arguments- these are optional and distinguished by -something
  parser.add_argument( '-v', action = 'store_true', dest = 'be_verbose',
                       help = 'Should BuoyBoy pretend he is called ChattyCathy?' )

  # Positional arguments- these are not identified by a flag.  Rather their meaning is
  # inferred from their position in the command line.
  parser.add_argument( 'southernLatitude', metavar = 'SouthernLatitude', type = float,
                       help = 'The southern latitudinal boundary of the data to be fetched.')
  parser.add_argument( 'northernLatitude', metavar = 'NorthernLatitude', type = float,
                       help = 'The northern latitudinal boundary of the data to be fetched.')
  parser.add_argument( 'westernLongitude', metavar = 'WesternLongitude', type = float,
                       help = 'The western longitudinal boundary of the data to be fetched.')
  parser.add_argument( 'easternLongitude', metavar = 'EasternLongitude', type = float,
                       help = 'The eastern longitudinal boundary of the data to be fetched.')
  parser.add_argument( 'startTime', metavar = 'StartTime', type = ISO_datestring,
                        help = '''The starting time for data you wish to download. Must be in the 
                        following format "month/day/year hour:minute:second"''' )
  parser.add_argument( 'stopTime', metavar = 'StopTime', type = ISO_datestring,
                        help = '''The end of the time range for which data is to be downloaded. 
                        Uses the same format as described above.''' ) 
  parser.add_argument( 'resolution', metavar = 'Resolution', type = str,
                        help = '''What resolution grid should be fetched, typically "6km" is used
                        and is the only resolution available in the Humboldt domain.''' ) 

  args = parser.parse_args()
  return args


if __name__ == '__main__':
  """
  This is the actual script part.  Building a script file this way allows it to be used
  as both a command line tool and a python library.  Then other Python scripts can import
  functions from this one without running the script.
  """
  
  args = processArgs()

  print "\n\nFetching data between [" + str(args.southernLatitude) + ", " + str(args.westernLongitude) + "] to ["  \
    + str(args.northernLatitude) + ", " + str(args.easternLongitude)+ "] from " + str(args.startTime) + " to " +   \
    str(args.stopTime) + " at a resolution of " + str(args.resolution) + "\n"

  currentRecords = HFRadar.fetchRecords( args.northernLatitude, args.southernLatitude, args.westernLongitude, \
      args.easternLongitude, args.startTime, args.stopTime, args.resolution )
  """
  Again, a useful command for development at the interpreter command line:
  currentRecords = HFRadar.fetchRecords(42,38,-128,-123,ISO_datestring("2010-07-25 00:00:00"),ISO_datestring("2010-07-26 00:00:00"),"6km")
  """
  HFRadar.commitToDB( currentRecords )
  #for record in currentRecords:
    #print record
    #print "--"
