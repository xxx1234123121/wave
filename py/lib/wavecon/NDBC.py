"""
Overview
--------

This module provides an interface to data stored at the National Buoy
Data Center (`NDBC`_).

**Development Status:**
  **Last Modified:** July 24, 2010 by Charlie Sharpsteen


.. _NDBC: http://www.ndbc.noaa.gov/

"""


from datetime import datetime

import urllib
import urllib2

import re

from functools import partial
from itertools import chain

from geoalchemy import WKTSpatialElement

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

BuoySource = DBman.accessTable( _DBconfig, 'tblsource' )
WindRecord = DBman.accessTable( _DBconfig, 'tblwind' )
WaveRecord = DBman.accessTable( _DBconfig, 'tblwave' )

_session = DBman.startSession( _DBconfig )


#---------------------------------------------------------------------
#  Data Retrieval
#---------------------------------------------------------------------
def fetchRecords( buoyNum, startTime, stopTime, dataType,
    verbose = False ):

  # Determine the years that need to be downloaded.
  timeSpan = range( startTime.year, stopTime.year + 1 )

  fetchData = partial( getData, 
    buoyNum = buoyNum, dataType = dataType )

  dataSets = [ rawToRecords( data, dataType ) for data 
    in ( fetchData( year ) for year in timeSpan )
    if NDBCGaveData(data) 
  ]

  # dataSets contains a list of records- one list for each year.
  # Flatten them into a single list containing all records.
  records = [ record for record in chain.from_iterable( dataSets ) ]
  # records = [ associateWithBuoy( record, buoyNum ) for record 
  #   in itertools.chain.from_iterable( dataSets )
  #   if isInsideTimespan( record.datetime, 
  #     startTime, stopTime ) ]

  return records


def getData( year, buoyNum, dataType ):
  BASE_URL = "http://www.ndbc.noaa.gov/view_text_file.php"
  PARAMS = {

    'meteorological' : { 
      'fileSep' : 'h', 
      'dataDir' : "data/historical/stdmet/" 
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

  NDBC = urllib2.urlopen( "{}?{}".format( BASE_URL, urlData ) )
  data = NDBC.read()
  NDBC.close()

  return data


def NDBCGaveData( responseString ):
  if 'Unable to access' in responseString:
    return False
  else:
    return True

def rawToRecords( rawData, dataType ):
  # Need to use re.split('\s+',line) instead of line.split(' ') because
  # there is a variable amount of whitespace seperating elements.
  parsedData = [ re.split('\s+', line) for line in rawData.splitlines()
    if not line.startswith('#') ]

  if dataType == 'meteorological':
    records = [(
        WindRecord( 
          winDateTime =  datetime( *[int(x) for x in line[0:5]] ),
          winDirection = float(line[5]),
          winSpeed = float(line[6])
        ),
        WaveRecord(
          wavDateTime =  datetime( *[int(x) for x in line[0:5]] ),
          wavHeight = float(line[8]),
          wavPeakDir = float(line[9]),
          wavPeakPeriod = float(line[11])
        ) 
      ) for line in parsedData ]
  else:
    raise TypeError

  return records


#---------------------------------------------------------------------
#  Database Interaction 
#---------------------------------------------------------------------
def getBuoyFromDB( buoyNum ):
  buoy = _session.query(BuoySource)\
      .filter( BuoySource.srcname == getBuoyName( buoyNum ) ).first()

  if buoy:
    return buoy
  else:
    # A record for this buoy does not exist in the DB. Create it.
    buoy = BuoySource( srcName = getBuoyName( buoyNum ) )

    _session.add( buoy )
    _session.commit()

    return buoy

def getBuoyID( buoyNum ):
  id = getBuoyFromDB( buoyNum ).srcid
  return id


def associateWithBuoy( record, buoyNum ):
  record.location = getBuoyLoc( buoyNum, asWKT = True )
  record.sourceid = getBuoyID( buoyNum )

  return record
    

def commitToDB( records ):
  _session.add_all( records )
  _session.commit()

  return None



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
  buoyLoc = BUOY_META[ str(buoyNum) ]['location']
  if asWKT:
    return WKTSpatialElement( "POINT({} {})".format(*buoyLoc) )
  else:
    return buoyLoc


def isInsideTimespan( aDate, startTime, stopTime ):
  if startTime <= aDate and stopTime >= aDate:
    return True
  else:
    return False
