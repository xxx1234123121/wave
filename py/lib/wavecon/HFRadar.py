"""
Overview
--------

This module provides an interface to data stored at the Integrated Ocean Observing System

**Development Status:**
  **Last Modified:** July 26, 2010 by Colin Sheppard

"""

import time

from math import atan2
from math import pi
from math import isnan

import datetime
from datetime import datetime
from numpy import *

import urllib
import urllib2

import re

import functools
import itertools

from geoalchemy import WKTSpatialElement


"""
For developmenet purposes: if not running as a library, execute the following here:

import sys
from os import path
scriptLocation = path.dirname(path.abspath("./HFRadarCurrent.py"))
waveLibs = path.abspath(path.join( scriptLocation, '..' ))
sys.path.insert( 0, waveLibs )
"""

from wavecon import DBman
from wavecon.config import DBconfig as _DBconfig

from dap.client import open


#---------------------------------------------------------------------
#  Metadata and Other Constants
#---------------------------------------------------------------------

HF_CURRENT_META = {

  '6km' : {
    'url' : 'http://sdf.ndbc.noaa.gov/thredds/dodsC/hfradar_uswc_6km'
  }

}

Source = DBman.accessTable( _DBconfig, 'tblsource' )
SourceType = DBman.accessTable( _DBconfig, 'tblsourcetype' )
CurrentRecord = DBman.accessTable( _DBconfig, 'tblcurrent' )

_session = DBman.startSession( _DBconfig )


#---------------------------------------------------------------------
#  Data Retrieval
#---------------------------------------------------------------------
def fetchRecords( north, south, west, east, startTime, stopTime, resolution,
    verbose = False ):

  records = getData( north, south, west, east, startTime, stopTime, resolution)
  return records

def getData( north, south, west, east, startTime, stopTime, resolution ):
  url = HF_CURRENT_META[ resolution ]['url']
  dataset = open(url)

  allLons = dataset.lon[:]
  allLats = dataset.lat[:]
  allTimes = dataset.time[:]
  xIndex = array([i for i,lon in enumerate(allLons) if lon>west and lon<east])
  yIndex = array([i for i,lat in enumerate(allLats) if lat>south and lat<north])
  tIndex = array([i for i,t in enumerate(allTimes) if t>time.mktime(startTime.timetuple()) and t<time.mktime(stopTime.timetuple()) ])
  lons = [allLons[i] for i in xIndex]
  lats = [allLats[i] for i in yIndex]
  times = [allTimes[i] for i in tIndex]

  u = dataset.u[min(tIndex):max(tIndex),min(yIndex):max(yIndex),min(xIndex):max(xIndex)]
  v = dataset.v[min(tIndex):max(tIndex),min(yIndex):max(yIndex),min(xIndex):max(xIndex)]
  
  return rawToRecords(times,lats,lons,u,v,resolution)

def rawToRecords(times,lats,longs,u,v,resolution):
  vel = (u**2+v**2)**0.5
  dir = array(map(lambda x,y: dirMathToMet(180.0 * atan2(x,y)/pi),v.ravel(),u.ravel())).reshape(u.shape)

  records = [ 
    CurrentRecord(
      curDateTime = datetime.fromtimestamp(times[t]),
      curLocation = WKTSpatialElement('POINT('+str(lat)+' '+str(lon)+')'),
      curSpeed = float(vel[t,y,x]),
      curDirection = float(dir[t,y,x])
    ) for t,time in enumerate(times) if t < len(times)-1
    for x,lon in enumerate(longs) if x < len(longs)-1
    for y,lat in enumerate(lats) if y < len(lats)-1 ]

  return [associateWithSource(record,resolution) for record in records if not (isnan(record.curspeed) or isnan(record.curdirection))]


#---------------------------------------------------------------------
#  Database Interaction 
#---------------------------------------------------------------------
def getSourceTypeFromDB( typeName ):
  srcType = _session.query(SourceType)\
      .filter( SourceType.sourcetypename == typeName ).first()

  if srcType:
    return srcType 
  else:
    # A record for this source type does not exist in the DB. Create it.
    srcType = SourceType( sourceTypeName = typeName)

    _session.add( srcType )
    _session.commit()

    return srcType

def getSourceFromDB( resolution ):
  src = _session.query(Source)\
      .filter( Source.srcname == 'HFRadar-'+resolution ).first()

  if src:
    return src 
  else:
    # A record for this source does not exist in the DB. Create it. First find the source type
    srcType = getSourceTypeFromDB( 'HFRadar' )
    src = Source( srcName = 'HFRadar-'+resolution, srcSourceTypeID=srcType.sourcetypeid )

    _session.add( src )
    _session.commit()

    return src

def getSourceID( resolution ):
  id = getSourceFromDB( resolution ).srcid
  return id


def associateWithSource( record, resolution ):
  record.sourceid = getSourceID( resolution )

  return record
    

def commitToDB( records ):
  _session.add_all( records )
  _session.commit()

  return None



#---------------------------------------------------------------------
#  Utility Functions
#---------------------------------------------------------------------
def isInsideTimespan( aDate, startTime, stopTime ):
  if startTime <= aDate and stopTime >= aDate:
    return True
  else:
    return False

def dirMathToMet(math):
  met = 90 - math
  while met<0:
    met += 360
  while met>=360:
    met -= 360
  return met
