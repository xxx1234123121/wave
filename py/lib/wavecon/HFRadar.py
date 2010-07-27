"""
Overview
--------

This module provides an interface to data stored at the Integrated Ocean Observing System

**Development Status:**
  **Last Modified:** July 26, 2010 by Colin Sheppard


.. _NDBC: http://www.ndbc.noaa.gov/

"""

import time

import datetime

import urllib
import urllib2

import re

import functools
import itertools

from geoalchemy import WKTSpatialElement

from wavecon import DBman
from wavecon.config import DBconfig as _DBconfig

from dap.client import open


#---------------------------------------------------------------------
#  Metadata and Other Constants
#---------------------------------------------------------------------

HF_CURRENT_META = {

  '6km' : {
    'url' : 'http://sdf.ndbc.noaa.gov:8080/thredds/dodsC/hfradar_uswc_6km'
  }

}

Source = DBman.accessTable( _DBconfig, 'tblsource' )
CurrentRecord = DBman.accessTable( _DBconfig, 'tblcurrent' )

_session = DBman.startSession( _DBconfig )


#---------------------------------------------------------------------
#  Data Retrieval
#---------------------------------------------------------------------
def fetchRecords( north, south, west, east, startTime, stopTime, 
    verbose = False ):

  fetchData = getData( north, south, west, east, startTime, stopTime, dataType )
    buoyNum = buoyNum, dataType = dataType )

"""
  dataSets = [ rawToRecords( data, dataType ) for data 
    in [fetchData( year ) for year in timeSpan]
    if NDBCGaveData(data) 
  ]

  # dataSets contains a list of records- one list for each year.
  # Flatten them into a single list containing all records.
  records = [ associateWithBuoy( record, buoyNum ) for record 
    in itertools.chain.from_iterable( dataSets )
    if isInsideTimespan( record.datetime, 
      startTime, stopTime ) ]

"""
  return records



def getData( north, south, west, east, startTime, stopTime, dataType ):
  url = HF_CURRENT_META[ dataType ]['url']
  dataset = open(url)

  allLons = dataset.lon[:]
  allLats = dataset.lat[:]
  allTimes = dataset.time[:]
  xIndex = [i for i,lon in enumerate(allLons) if lon>west and lon<east]
  yIndex = [i for i,lat in enumerate(allLats) if lat>south and lat<north]
  tIndex = [i for i,t in enumerate(allTimes) if t>time.mktime(startTime.timetuple()) and t<time.mktime(stopTime.timetuple()) ]
  lons = [allLons[i] for i in xIndex]
  lats = [allLats[i] for i in yIndex]
  times = [allTimes[i] for i in tIndex]

  u = dataset.u[min(tIndex):max(tIndex),min(yIndex):max(yIndex),min(xIndex):max(xIndex)]
  v = dataset.v[min(tIndex):max(tIndex),min(yIndex):max(yIndex),min(xIndex):max(xIndex)]
  
  return [times,lats,lons,u,v]


"""
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

  if dataType == 'wind':
    records = [ 
      WindRecord( 
        winDateTime =  datetime.datetime(*[int(x) for x in line[0:5]]),
        winDirection = float(line[5]),
        winSpeed = float(line[6])
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

"""
