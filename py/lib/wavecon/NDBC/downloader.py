"""
Overview
--------

This module provides an interface to data stored at the National Buoy
Data Center (`NDBC`_).

**Development Status:**
  **Last Modified:** August 16, 2010 by Charlie Sharpsteen


.. _NDBC: http://www.ndbc.noaa.gov/

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from datetime import datetime, timedelta
from collections import namedtuple

import urllib
import urllib2

import re

from itertools import chain

#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from geoalchemy import WKTSpatialElement

#------------------------------------------------------------------------------
#  Imports from other NDBC submodules
#------------------------------------------------------------------------------
from .globals import *


#------------------------------------------------------------------------------
#  Metadata, Object Classes and Other Constants
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#  Data Retrieval
#------------------------------------------------------------------------------
def fetchBuoyRecords( buoyNum, startTime, stopTime, verbose = False ):

  print startTime.isoformat()
  print stopTime.isoformat()

  # Determine the years that need to be downloaded.
  timeSpan = range( startTime.year, stopTime.year + 1 )

  metData =  fetchRecords( timeSpan, buoyNum, 'meteorological' )
  densityData = fetchRecords( timeSpan, buoyNum, 'specDensity' )

  # Unfortunately, there is not always corresponding spectra data available for
  # wave height, peak direction or frequency given by the meterological data, or
  # vice-versa.  The solution is to first filter each list and return the
  # records that fall within the requested time range along with a seperate list
  # of the datestamps.  The datestamps may then be intersected to locate wave
  # and spectra records that can be combined.
  windRecords, waveRecords, waveTimestamps = zip(*[
    ( wind, wave, wave['datetime'] )
    for wind, wave in metData
    if isInsideTimespan( wind['datetime'], startTime, stopTime )
  ])

  if len( densityData ) > 0:
    densityData, densityTimestamps = zip(*[
      ( density, density['datetime'] ) 
      for density in densityData 
      if isInsideTimespan( density['datetime'], startTime, stopTime )
    ])

  waveRecords = joinWithSpectra( waveRecords, waveTimestamps, 
      densityData, densityTimestamps )

  return windRecords, waveRecords


def fetchRecords( timeSpan, buoyNum, dataType ):
  records = [
    rawToRecords( data, buoyNum, dataType )
    for data in [ fetchData( year, buoyNum, dataType )
      for year in timeSpan ]
    if NDBCGaveData(data) ]

  # The above list comprehension returns a list of lists with each
  # sublist containing records for one year.  The chain function is
  # used to flatten the list of lists into a single list.
  return list(chain.from_iterable( records ))

def fetchData( year, buoyNum, dataType ):
  BASE_URL = "http://www.ndbc.noaa.gov/view_text_file.php"
  PARAMS = {

    'meteorological' : {
      'fileSep' : 'h',
      'dataDir' : "data/historical/stdmet/"
    },

    'specDensity' : {
      'fileSep' : 'w',
      'dataDir' : 'data/historical/swden/'
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

def rawToRecords( rawData, buoyNum, dataType ):
  # Need to use re.split('\s+',line) instead of line.split(' ') because
  # there is a variable amount of whitespace separating elements.
  rawData = rawData.splitlines()

  if dataType == 'specDensity':
    binLine = re.split( '\s+', rawData.pop(0) )

  parsedData = [ re.split('\s+', line) for line in rawData
    if not line.startswith('#') and not line.startswith('YY') ]

  # Ugly hack #1: NDBC added a "minutes" column in 2005- this code
  # compensates for the varying column offsets.
  if int(parsedData[0][0]) >= 2005:
    C = 5
  else:
    C = 4

  if dataType == 'meteorological':  records = [
      (
        {
          'buoyNumber': buoyNum,
          'datetime': dateFromRaw( line[0:C] ),
          'winDirection': float(line[C]),
          'winSpeed': float(line[C+1])
        },
        { 
          'buoyNumber': buoyNum,
          'datetime':  dateFromRaw( line[0:C] ),
          'wavHeight': float(line[C+3]),
          'wavPeakDir': float(line[C+4]),
          'wavPeakPeriod': float(line[C+6])
        }
      )
      for line in parsedData
    ]
  elif dataType == 'specDensity':
    records = [
      { 
        'buoyNumber': buoyNum,
        'datetime': dateFromRaw( line[0:C] ),
        'densityBins': [ float(x) for x in binLine[C:] ], 
        # Not the most efficient to store a copy of the bins in each record but
        # this allows the bins to change over time.
        'density': [ float(x) for x in line[C:] ]
      }
      for line in parsedData
    ]
  else:
    raise TypeError

  return records


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

def joinWithSpectra( waveRecords, waveTimestamps,
    spectraRecords, spectraTimestamps
):

  waveToJoin, waveToPass = splitWaveRecords( waveRecords, waveTimestamps )
  spectraToJoin, spectraToPass = splitWaveRecords( spectraRecords, spectraTimestamps )

  for wave, spectra in zip( waveToJoin, spectraToJoin ):
    wave.update( spectra )

  return waveToPass + waveToJoin + spectraToPass

def splitWaveRecords( records, timestamps ):
  recordsToJoin = [
    record
    for record in records
    if record['datetime'] in timestamps
  ]

  recordsToPass = [
    record
    for record in records
    if record['datetime'] not in timestamps
  ]

  return recordsToJoin, recordsToPass

def dateFromRaw( line ):
  # Ugly hack #2: This one is truly hideous- not all hourly
  # observations begin on the hour.  For example, starting in the
  # middle of 2008 the meteorological observations for buoy #46022 are
  # recorded 10 minutes before the hour, while the spectral
  # observations continue to be recorded on the hour.
  #
  # This hack is so ugly because I am assuming the following thing:
  #
  # 1) All time differences are negative- I.E. if the minutes column
  # reads "50" instead of "00" then there is a time shift of -10
  # minutes, not +50 minutes.  So 10 minutes is added to the minute
  # count. This could be royally screwed up- I would have to compare
  # against the continuous observations to make sure.
  line = [int(x) for x in line]
  if len(line) == 5 and line[-1] != 0:
    return datetime(*line) + timedelta( minutes = (60 - line[-1]) )
  else:
    return datetime(*line)
