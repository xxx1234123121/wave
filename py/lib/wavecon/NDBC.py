"""
Overview
--------

This module provides an interface to data stored at the National Buoy
Data Center (`NDBC`_).

**Development Status:**
  **Last Modified:** July 23, 2010 by Charlie Sharpsteen


.. _NDBC: http://www.ndbc.noaa.gov/

"""
import datetime

import urllib
import urllib2

import re

import functools
import itertools

#---------------------------------------------------------------------
#  Metadata
#---------------------------------------------------------------------

#---------------------------------------------------------------------
#  Data Retrieval
#---------------------------------------------------------------------
def fetchFromNDBC( buoyNum, startTime, stopTime, dataType,
    verbose = False ):

  # Determine the years that need to be downloaded.
  timeSpan = range( startTime.year, stopTime.year + 1 )

  fetchData = functools.partial( NDBCGetData, 
    buoyNum = buoyNum, dataType = dataType )

  dataSets = [ NDBCrawToRecords(data) for data in [fetchData( year ) for year in timeSpan]
    if NDBCGaveData(data) ]

  # dataSets contains a list of records- one list for each year.
  # Flatten them into a single list containing all records.
  data = [ record for record in itertools.chain.from_iterable( dataSets )
    if isInsideTimespan( record['dateTime'], startTime, stopTime ) ]

  return data


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
  # E.g slashes, /, will become %2. The urllib.unquote function fixes this.
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

def NDBCrawToRecords( rawData ):
  # Need to use re.split('\s+',line) instead of line.split(' ') because
  # there is a variable amount of whitespace seperating elements.
  parsedData = [ re.split('\s+', line) for line in rawData.splitlines()
    if not line.startswith('#') ]

  records = [ 
    { 
      'dateTime' : datetime.datetime(*[int(x) for x in line[0:5]]),
      'winDirection' : float(line[5]),
      'winSpeed' : float(line[6])
    } 
    for line in parsedData ]

  return records


#---------------------------------------------------------------------
#  Utility Functions
#---------------------------------------------------------------------
def isInsideTimespan( aDate, startTime, stopTime ):
  if startTime <= aDate and stopTime >= aDate:
    return True
  else:
    return False
