"""
Overview
--------

This module provides an interface to data stored at the National Buoy
Data Center (`NDBC`_).

**Development Status:**
  **Last Modified:** November 5, 2010 by Charlie Sharpsteen


.. _NDBC: http://www.ndbc.noaa.gov/

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from datetime import datetime, timedelta

import urllib
import urllib2

import re

from itertools import chain

from math import pi, cos, radians

#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  Imports from other NDBC submodules
#------------------------------------------------------------------------------
from .globals import *


#------------------------------------------------------------------------------
#  Data Retrieval
#------------------------------------------------------------------------------
def fetchBuoyRecords( buoyNum, startTime, stopTime, num_dir_bins, verbose = False ):

  if startTime > stopTime:
    raise RuntimeError(
      """You specified a start time of {0} and a stop time of {1}.  The stop time
      must be later than the start time.""".format(
        startTime.isoformat(), stopTime.isoformat()
      )
    )

  # Determine the years that need to be downloaded.
  timeSpan = calcDownloadDates( startTime, stopTime )

  metData =  fetchRecords( timeSpan, buoyNum, 'meteorological' )
  densityData = fetchRecords( timeSpan, buoyNum, 'specDensity' )
  alpha1Data = fetchRecords( timeSpan, buoyNum, 'directionAlpha1' )
  alpha2Data = fetchRecords( timeSpan, buoyNum, 'directionAlpha2' )
  r1Data = fetchRecords( timeSpan, buoyNum, 'directionR1')
  r2Data = fetchRecords( timeSpan, buoyNum, 'directionR2' )

  # Unfortunately, there is not always corresponding spectra data available for
  # wave height, peak direction or frequency given by the meterological data, or
  # vice-versa.  The solution is to first filter each list and return the
  # records that fall within the requested time range along with a seperate list
  # of the datestamps.  The datestamps may then be intersected to locate wave
  # and spectra records that can be combined.
  try:
    windRecords, waveRecords, waveTimestamps = zip(*[
      ( wind, wave, wave['datetime'] )
      for wind, wave in metData
      if isInsideTimespan( wind['datetime'], startTime, stopTime )
    ])
  except:
    # Check to see if we got meteorlogical data.  If we didn't, we probably did
    # not get any data so wipe out with an error.
    raise RuntimeError(
      """Did not recieve any meterological data from NDBC for buoy {0}, for the
      time period starting on {1} and ending on {2}.  It is likely that data
      either does not exist or there was an error in parsing the NDBC
      output.""".format( 
        buoyNum, startTime.isoformat(), stopTime.isoformat() 
      )
    )

  if len( densityData ) > 0:
    densityData, densityTimestamps = zip(*[
      ( density, density['datetime'] ) 
      for density in densityData 
      if isInsideTimespan( density['datetime'], startTime, stopTime )
    ])

    waveRecords = joinWithSpectra( waveRecords, waveTimestamps, 
      densityData, densityTimestamps )

  if len( alpha1Data ) > 0:
    alpha1Data, alpha1Timestamps = zip(*[
      ( alpha1, alpha1['datetime'] ) 
      for alpha1 in alpha1Data 
      if isInsideTimespan( alpha1['datetime'], startTime, stopTime )
    ])

    waveRecords = joinWithSpectra( waveRecords, waveTimestamps, 
      alpha1Data, alpha1Timestamps )

  if len( alpha2Data ) > 0:
    alpha2Data, alpha2Timestamps = zip(*[
      ( alpha2, alpha2['datetime'] ) 
      for alpha2 in alpha2Data 
      if isInsideTimespan( alpha2['datetime'], startTime, stopTime )
    ])

    waveRecords = joinWithSpectra( waveRecords, waveTimestamps, 
      alpha2Data, alpha2Timestamps )

  if len( r1Data ) > 0:
    r1Data, r1Timestamps = zip(*[
      ( r1, r1['datetime'] ) 
      for r1 in r1Data 
      if isInsideTimespan( r1['datetime'], startTime, stopTime )
    ])

    waveRecords = joinWithSpectra( waveRecords, waveTimestamps, 
      r1Data, r1Timestamps )

  if len( r2Data ) > 0:
    r2Data, r2Timestamps = zip(*[
      ( r2, r2['datetime'] ) 
      for r2 in r2Data 
      if isInsideTimespan( r2['datetime'], startTime, stopTime )
    ])

    waveRecords = joinWithSpectra( waveRecords, waveTimestamps, 
      r2Data, r2Timestamps )

  waveRecords = [ collapseSpectra(record, num_dir_bins)
    for record in waveRecords ]

  return windRecords, waveRecords


def fetchRecords( timeSpan, buoyNum, dataType ):
  records = [
    rawToRecords( data, buoyNum, dataType )
    for data in [ fetchData( time, buoyNum, dataType )
      for time in timeSpan ]
    if NDBCGaveData(data) ]

  # The above list comprehension returns a list of lists with each
  # sublist containing records for one year.  The chain function is
  # used to flatten the list of lists into a single list.
  return list(chain.from_iterable( records ))


def fetchData( time, buoyNum, dataType ):
  BASE_URL = "http://www.ndbc.noaa.gov/view_text_file.php"
  PARAMS = {

    'meteorological' : {
      'fileSep' : 'h',
      'dataDir' : "stdmet"
    },

    'specDensity' : {
      'fileSep' : 'w',
      'dataDir' : 'swden'
    },

    'directionAlpha1' : {
      'fileSep' : 'd',
      'dataDir' : 'swdir'
    },

    'directionAlpha2' : {
      'fileSep' : 'i',
      'dataDir' : 'swdir2'
    },

    'directionR1' : {
      'fileSep' : 'j',
      'dataDir' : 'swr1'
    },

    'directionR2' : {
      'fileSep' : 'k',
      'dataDir' : 'swr2'
    }

  }

  case = PARAMS[ dataType ]

  if time[0] == 'year':
    dataDict = {
      'filename' : "{0}{1}{2}.txt.gz".format( buoyNum, case['fileSep'], time[1] ),
      'dir' : "data/historical/{0}/".format( case['dataDir'] )
    }
  elif time[0] == 'month':
    year = datetime.now().year
    month = datetime(2000,time[1],1).strftime('%b')
    dataDict = {
      'filename' : "{0}{1}{2}.txt.gz".format( buoyNum, time[1], year ),
      'dir' : "data/{0}/{1}/".format( case['dataDir'], month )
    }

  # Annoying thing about Python's URL encoder- it will ALWAYS substitute characters.
  # E.g slashes, /, will become %2. The urllib.unquote function fixes this.
  urlData = urllib.unquote(urllib.urlencode( dataDict ))

  NDBC = urllib2.urlopen( "{0}?{1}".format( BASE_URL, urlData ) )
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

  if not dataType == 'meteorological':
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
          'type': 'windRecords',
          'buoyNumber': buoyNum,
          'datetime': dateFromRaw( line[0:C] ),
          'winDirection': float(line[C]),
          'winSpeed': float(line[C+1])
        },
        { 
          'type': 'waveRecords',
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
        'type': 'waveRecords',
        'buoyNumber': buoyNum,
        'datetime': dateFromRaw( line[0:C] ),
        'densityBins': [ float(x) for x in binLine[C:] ], 
        # Not the most efficient to store a copy of the bins in each record but
        # this allows the bins to change over time.
        'density': [ float(x) for x in line[C:] ]
      }
      for line in parsedData
    ]
  elif dataType == 'directionAlpha1':
    records = [
      { 
        'type': 'waveRecords',
        'buoyNumber': buoyNum,
        'datetime': dateFromRaw( line[0:C] ),
        'directionAlpha1Bins': [ float(x) for x in binLine[C:] ], 
        'directionAlpha1': [ float(x) for x in line[C:] ]
      }
      for line in parsedData
    ]
  elif dataType == 'directionAlpha2':
    records = [
      { 
        'type': 'waveRecords',
        'buoyNumber': buoyNum,
        'datetime': dateFromRaw( line[0:C] ),
        'directionAlpha2Bins': [ float(x) for x in binLine[C:] ], 
        'directionAlpha2': [ float(x) for x in line[C:] ]
      }
      for line in parsedData
    ]
  elif dataType == 'directionR1':
    records = [
      { 
        'type': 'waveRecords',
        'buoyNumber': buoyNum,
        'datetime': dateFromRaw( line[0:C] ),
        'directionR1Bins': [ float(x) for x in binLine[C:] ], 
        'directionR1': [ float(x) for x in line[C:] ]
      }
      for line in parsedData
    ]
  elif dataType == 'directionR2':
    records = [
      { 
        'type': 'waveRecords',
        'buoyNumber': buoyNum,
        'datetime': dateFromRaw( line[0:C] ),
        'directionR2Bins': [ float(x) for x in binLine[C:] ], 
        'directionR2': [ float(x) for x in line[C:] ]
      }
      for line in parsedData
    ]
  else:
    raise TypeError

  return records


#---------------------------------------------------------------------
#  Utility Functions
#---------------------------------------------------------------------
def calcDownloadDates( startTime, stopTime ):
  # NDBC data is stored in yearly chunks for historical data and monthly chunks
  # for current data.  This script determines which chunks need to be downloaded
  # to cover the given time span.  If the startTime and stopTime occur before
  # the current year, a download is executed for each year.  If the startTime or
  # stopTime fall within the current year, a download is executed for each
  # month in the year.
  
  now = datetime.now()
  getChunks = []

  if startTime.year < now.year and stopTime.year == now.year:
    getYears = range( startTime.year, stopTime.year )
    getChunks += zip( ['year'] * len(getYears), getYears )
  elif startTime.year < now.year and stopTime.year < now.year:
    getYears = range( startTime.year, stopTime.year + 1 )
    getChunks += zip( ['year'] * len(getYears), getYears )

  if startTime.year < now.year and stopTime.year == now.year:
    getMonths = range( 1, stopTime.month + 1 )
    getChunks += zip( ['month'] * len(getMonths), getMonths )
  if startTime.year == now.year and stopTime.year == now.year:
    getMonths = range( startTime.month, stopTime.month + 1 )
    getChunks += zip( ['month'] * len(getMonths), getMonths )

  return getChunks



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
    # Find the bins in the spectral record.
    binKey = [key for key in spectra.keys()
      if key.endswith('Bins')].pop()

    # If the wave record does not have frequency bins for spectra, we create
    # them using the bins in the wave record.
    if 'frequencyBins' not in wave:
      wave['frequencyBins'] = spectra[binKey]

    else:
      # Otherwise, we check to ensure the wave record frequency bins and the
      # spectra frequency bins are the same.
      binDiff = set.difference( set(wave['frequencyBins']),
        set(spectra[binKey]) )

      if not len(binDiff) == 0:
        raise RuntimeError('''Got a differing number of frequency bins for a
        wave record and a spectra record!''')

    del spectra[binKey]

    wave.update( spectra )

  return waveToJoin


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


def collapseSpectra( record, num_dir_bins ):
  WAVE_SPECTRA = [
    'density',
    'directionAlpha1',
    'directionAlpha2',
    'directionR1',
    'directionR2'
  ]

  if all([spectra in record for spectra in WAVE_SPECTRA]):
    # We have 5 disaggregated direction and density spectra---enough to make a
    # 2D spectra or to report them using an array.
    if num_dir_bins == 0:
      # Collapse the density and direction spectra into a single array.
      record['spectra'] = [record[spectra] for spectra in WAVE_SPECTRA]
      record['spectraType'] = '2D-aggregated'

    else:
      # First, we create the direction bins:
      dir_bins = linspace_list(0, 360, num_dir_bins)

      # First, we collapse the 5 vectors of spectra into a single vector of
      # tuples:
      #     (density, alpha1, alpha2, r1, r2)
      parameters = zip(*[record[spectra] for spectra in WAVE_SPECTRA]) 

      record['spectra'] = make2Dspectra(parameters, dir_bins)
      record['spectraType'] = '2D'
      record['directionBins'] = dir_bins

  elif 'density' in record:
    # We can only make a 1D spectra.
    record['spectra'] = record['density']
    record['spectraType'] = '1D'

  # Remove old information.
  for key in WAVE_SPECTRA:
    if key in record:
      del record[key]

  # Transform frequency bins to an array.
  record['frequencyBins'] = record['frequencyBins']

  return record


def make2Dspectra( parameters, dirBins ):
  # NDBC reports R1 and R2 scaled by 100
  spectra = [
      [ calc2Dspectra( density, alpha1, alpha2, r1 / 100, r2 / 100, angle )
      for density, alpha1, alpha2, r1, r2 in parameters ]
    for angle in dirBins ]

  return spectra


def calc2Dspectra( density, Alpha1, Alpha2, R1, R2, A, ):
  return density * (1/pi) * (
      0.5 +
      R1 * cos(radians( A - Alpha1 )) +
      R2 * cos(radians( 2 * (A - Alpha2) ))
    )


def linspace_list( ll, ul, n ):
  return [ ll + pos * (ul - ll)/(n-1) for pos in range(0,n)]

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

  # Check for two diget years:
  if line[0] < 1900 : line[0] += 1900

  if len(line) == 5 and line[-1] != 0:
    return datetime(*line) + timedelta( minutes = (60 - line[-1]) )
  else:
    return datetime(*line)
