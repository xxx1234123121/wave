#!/usr/bin/env python

import datetime

import urllib
import urllib2

import re

import functools

"""
-------------------------------------------------------------------
This script retrieves buoy data from the NDBC.

Version:       0.1.0
Author:        Charlie Sharpsteen <source@sharpsteen.net>
Last Modified: July 19, 2010 by Charlie Sharpsteen
-------------------------------------------------------------------
"""


"""
-------------------------------------------------------------------
   Data Retrieval
-------------------------------------------------------------------
"""
def fetchFromNDBC( buoyNum, startTime, stopTime, dataType, verbose = False ):

  # Determine the years that need to be downloaded.
  timeSpan = range( startTime.year, stopTime.year + 1 )

  fetchData = functools.partial( NDBCGetData, 
    buoyNum = buoyNum, dataType = dataType )

  dataSets = [ processNDBC(data) for data in [fetchData( year ) for year in timeSpan]
    if NDBCGaveData(data) ]

  return dataSets


def NDBCGetData( year, buoyNum, dataType ):
  BASE_URL = "http://www.ndbc.noaa.gov/view_text_file.php"
  PARAMS = {

    'wind' : { 
      'fileSep' : 'c', 
      'dataDir' : "data/historical/cwind/" 
    }

  }

  case = PARAMS[ dataType ]

  dataDict = { 
    'filename' : str( buoyNum ) + case['fileSep'] + str( year ) + '.txt.gz',
    'dir' : case['dataDir']
  }

  # Annoying thing about Python's URL encoder- it will ALWAYS substitute characters.
  # I.E slashes, /, will become %2. The urllib.unquote function fixes this.
  urlData = urllib.unquote(urllib.urlencode( dataDict ))

  NDBC = urllib2.urlopen( "%s?%s" % ( BASE_URL, urlData ) )
  data = NDBC.read()
  NDBC.close()

  return data


def NDBCGaveData( responseString ):
  if 'Unable to access' in responseString:
    return False
  else:
    return True

def processNDBC( rawData ):
  # Need to use re.split('\s+',line) instead of line.split(' ') because
  # there is a variable amount of whitespace seperating elements.
  parsedData = [ re.split('\s+', line) for line in rawData.splitlines()
    if not line.startswith('#') ]

  records = [ 
    { 
      'winDateTime' : datetime.datetime(*[int(x) for x in line[0:4]]),
      'winDirection' : float(line[5]),
      'winSpeed' : float(line[6])
    } 
    for line in parsedData ]

  return records

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

  args = parser.parse_args()
  return args

if __name__ == '__main__':
  """
  This is the actual script part.  Building a script file this way allows it to be used
  as both a command line tool and a python library.  Then other Python scripts can import
  functions from this one without running the script.
  """
  
  args = processArgs()

  print "\n\nHello, world!\n"

  urlTest = fetchFromNDBC( args.buoyNum, args.startTime, args.stopTime, 'wind' )

  print urlTest

