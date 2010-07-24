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

from wavecon import DBman
from wavecon.config import DBconfig as _DBconfig

#---------------------------------------------------------------------
#  Metadata and Other Constants
#---------------------------------------------------------------------

BUOY_META = {

  '46022' : {
    'location' : ( 40.749, -124.577 ),
    'type' : 'NDBC'
  },

  '46212' : {
    'location' : ( 40.753, -124.313 ),
    'type' : 'SCRIPPS'
  },

  '46244' : {
    'location' : ( 40.888, -124.357 ),
    'type' : 'SCRIPPS'
  }

}


#---------------------------------------------------------------------
#  Data Retrieval
#---------------------------------------------------------------------
def fetchFromNDBC( buoyNum, startTime, stopTime, dataType,
    verbose = False ):

  # Determine the years that need to be downloaded.
  timeSpan = range( startTime.year, stopTime.year + 1 )

  fetchData = functools.partial( NDBCGetData, 
    buoyNum = buoyNum, dataType = dataType )

  dataSets = [ NDBCrawToRecords(data) for data in 
    [fetchData( year ) for year in timeSpan]
    if NDBCGaveData(data) ]

  # dataSets contains a list of records- one list for each year.
  # Flatten them into a single list containing all records.
  data = [ record for record in itertools.chain.from_iterable( dataSets )
    if isInsideTimespan( record.dateTime(), startTime, stopTime ) ]

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
#  Database Interaction 
#---------------------------------------------------------------------
def getBuoyFromDB( buoyNum ):
  Buoy = DBman.accessTable( _DBconfig, 'tblsource' )
  session = DBman.startSession( _DBconfig )

  buoy = session.query(Buoy)\
      .filter( Buoy.srcname == getBuoyName( buoyNum ) ).first()

  if buoy:
    session.close()
    return buoy
  else:
    # A record for this buoy does not exist in the DB. Create it.
    buoy = Buoy( srcName = getBuoyName( buoyNum ) )

    session.add( buoy )
    session.commit()
    session.refresh( buoy )
    session.close()

    return buoy

def getBuoyID( buoyNum ):
  id = getBuoyFromDB( buoyNum ).srcid
  return id

#---------------------------------------------------------------------
#  Utility Functions
#---------------------------------------------------------------------
def getBuoyName( buoyNum ):
  buoyNum = str( buoyNum )
  try:
    name = "{}-{}".format( BUOY_META[buoyNum]['type'], buoyNum )
  except:
    print "There exists no buoy with the number: {}".format( buoyNum )
    raise

  return name


def getBuoyLoc( buoyNum, asWKT = False ):
  buoyLoc = BUOY_META[ str(buoyNum) ]
  if asWKT:
    return "POINT({} {})".format(*buoyLoc)
  else:
    return buoyLoc


def isInsideTimespan( aDate, startTime, stopTime ):
  if startTime <= aDate and stopTime >= aDate:
    return True
  else:
    return False
