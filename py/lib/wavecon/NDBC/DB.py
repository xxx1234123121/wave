"""
Overview
--------

This module provides routines for serializing data obtained by the data.py
module to a SQL database.

**Development Status:**
  **Last Modified:** August 25, 2010 by Charlie Sharpsteen


"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from sqlalchemy import or_
from sqlalchemy.sql.expression import cast
from sqlalchemy.dialects.postgresql import ARRAY, DOUBLE_PRECISION
from geoalchemy import WKTSpatialElement

#------------------------------------------------------------------------------
#  Imports from WaveConnect libraries
#------------------------------------------------------------------------------
from wavecon import DBman


#------------------------------------------------------------------------------
#  Metadata, Object Classes and Other Constants
#------------------------------------------------------------------------------
# Database setup
from wavecon.config import DBconfig as _DBconfig

BuoySource = DBman.accessTable( _DBconfig, 'tblsource' )
SourceTypeRecord = DBman.accessTable( _DBconfig, 'tblsourcetype' )
WindRecord = DBman.accessTable( _DBconfig, 'tblwind' )
WaveRecord = DBman.accessTable( _DBconfig, 'tblwave' )
SpectraRecord = DBman.accessTable( _DBconfig, 'tblspectra' )

_session = DBman.startSession( _DBconfig )

# Import NDBC global variables
from .globals import BUOY_META


#------------------------------------------------------------------------------
#  Forming and Committing Database Records
#------------------------------------------------------------------------------
def formDatabaseRecords( NDBCrecords ):
  recordType = NDBCrecords[0]['type']

  # Assuming all the records in the list are from the same buoy.
  buoyNum = NDBCrecords[0]['buoyNumber']
  buoyID = getBuoyID( buoyNum )
  buoyLocation = getBuoyLoc( buoyNum, asWKT = True )

  if recordType == 'windRecords':
    records = [
      makeWindRecord(
        record,
        buoyID,
        buoyLocation )
      for record in NDBCrecords
    ]

  elif recordType == 'waveRecords':
    records = [
      makeWaveRecord(
        record,
        buoyID,
        buoyLocation )
      for record in NDBCrecords
    ]

  else:
    raise TypeError("Do not know how do deal with records of type {0}!".format(
      recordType
    ))

  return records

def makeWindRecord( NDBCrecord, buoyID, buoyLocation ):
  record = WindRecord(
    winDateTime = NDBCrecord['datetime'],
    winDirection = NDBCrecord['winDirection'],
    winSpeed = NDBCrecord['winSpeed']
  )

  record.sourceid = buoyID
  record.location = buoyLocation

  return record

def makeWaveRecord( NDBCrecord, buoyID, buoyLocation ):
  record = WaveRecord(
    wavDateTime = NDBCrecord['datetime'],
  )

  if 'wavHeight' in NDBCrecord:
    record.wavheight = NDBCrecord['wavHeight']

  if 'wavPeakDir' in NDBCrecord:
    record.wavPeakDir = NDBCrecord['wavPeakDir']

  if 'wavPeakPeriod' in NDBCrecord:
    record.wavPeakDir = NDBCrecord['wavPeakPeriod']

  densityBins, directionBins = getBinsFromRecord( NDBCrecord )

  record.wavspectraid = getSpectraID( densityBins, directionBins )
  record.wavspectra = getSpectraFromRecord( NDBCrecord )

  record.sourceid = buoyID
  record.location = buoyLocation

  return record

def getBinsFromRecord( NDBCrecord ):
  WAVE_DIRECTION_BINS = [
    'directionAlpha1Bins',
    'directionAlpha2Bins',
    'directionR1Bins',
    'directionR2Bins'
  ]

  if 'densityBins' in NDBCrecord.keys():
    densityBins = NDBCrecord['densityBins']
  else:
    densityBins = None

  directionBins = [
    set(NDBCrecord[key])
    for key in NDBCrecord.keys()
    if key in WAVE_DIRECTION_BINS
  ]

  if len( directionBins ) == 0:
    # There were no direction bins.
    directionBins = None
  elif len(set.difference(*directionBins)) == 0:
    # There were many direction bins but they are all the same.  However they
    # were converted to sets, which destroys ordering.  Use one of the original
    # bin lists.
    directionBins = [
      NDBCrecord[key]
      for key in NDBCrecord.keys()
      if key in WAVE_DIRECTION_BINS
    ][0]
  else:
    # Need better error message. Should probably be logged.
    raise TypeError("Directional spectra have different bin ranges!")

  return densityBins, directionBins

def getSpectraFromRecord( NDBCrecord ):
  spectra = [ [],[],[],[],[] ]

  keys = NDBCrecord.keys()

  if 'density' in keys:
    spectra[0] = NDBCrecord['density']
  else:
    raise TypeError("No frequency spectra! Cowardly refusing to make a record!")

  if 'directionAlpha1' in keys:
    spectra[1] = NDBCrecord['directionAlpha1']
  else:
    spectra[1] = [-99] * len(spectra[0])

  if 'directionAlpha2' in keys:
    spectra[2] = NDBCrecord['directionAlpha2']
  else:
    spectra[2] = [-99] * len(spectra[0])

  if 'directionR1' in keys:
    spectra[3] = NDBCrecord['directionR1']
  else:
    spectra[3] = [-99] * len(spectra[0])

  if 'directionR2' in keys:
    spectra[4] = NDBCrecord['directionR2']
  else:
    spectra[4] = [-99] * len(spectra[0])

  return spectra

#------------------------------------------------------------------------------
#  Database Buoy Representation
#------------------------------------------------------------------------------
def associateWithBuoy( record, buoyID, buoyLocation ):
  record.sourceid = buoyID
  record.location = buoyLocation

  return record

def getBuoyID( buoyNum ):
  id = getBuoyFromDB( buoyNum ).srcid
  return id

def getBuoyLoc( buoyNum, asWKT = False ):
  buoyLoc = BUOY_META[ str(buoyNum) ]['location']
  if asWKT:
    return WKTSpatialElement( "POINT({0} {1})".format(*buoyLoc) )
  else:
    return buoyLoc

def getBuoyFromDB( buoyNum ):
  buoy = _session.query(BuoySource).filter( 
    BuoySource.srcname == getBuoyName( buoyNum ) 
  ).first()

  if buoy:
    return buoy
  else:
    # A record for this buoy does not exist in the DB. Create it.
    buoy = BuoySource( 
      srcName = getBuoyName( buoyNum ), 
      srcSourceTypeID = getSourceTypeID( buoyNum )
    )

    _session.add( buoy )
    _session.commit()

    return buoy

def getBuoyName( buoyNum ):
  buoyNum = str( buoyNum )
  try:
    name = "{0}-{1}".format( BUOY_META[buoyNum]['type'], buoyNum )
  except:
    print "There exists no buoy with the number: {0}".format( buoyNum )
    raise

  return name

def getBuoySourceType( buoyNum ):
  buoyNum = str( buoyNum )

  try:
    buoyType = "{0}-{1}".format( "NDBC", BUOY_META[buoyNum]['type'] )
  except:
    print "There exists no buoy with the number: {0}".format( buoyNum )
    raise

  return buoyType


#------------------------------------------------------------------------------
#  Database SourceType Representation
#------------------------------------------------------------------------------
def getSourceTypeID( buoyNum ):
  buoyType = _session.query(SourceTypeRecord).filter( 
    SourceTypeRecord.sourcetypename == getBuoySourceType( buoyNum ) 
  ).first()

  if buoyType:
    return buoyType.id
  else:
    # A record for this buoy does not exist in the DB. Create it.
    buoyType = SourceTypeRecord( sourceTypeName = getBuoySourceType( buoyNum ) )

    _session.add( buoyType )
    _session.commit()

    return buoyType.id


#------------------------------------------------------------------------------
#  Database Spectra Representation
#------------------------------------------------------------------------------
def getSpectraID( freqBins = None, dirBins = None ):
  spectra = _session.query(SpectraRecord).filter(or_(
    SpectraRecord.spectrafreq == cast( freqBins, ARRAY(DOUBLE_PRECISION) ),
    SpectraRecord.spectradir == cast( dirBins, ARRAY(DOUBLE_PRECISION) )
  )).first()

  if spectra:
    return spectra.id
  else:
    # Create a record for the spectra.
    spectra = SpectraRecord( spectraFreq = freqBins, spectraDir = dirBins )

    _session.add( spectra )
    _session.commit()

    return spectra.id


#---------------------------------------------------------------------
#  Database Interaction
#---------------------------------------------------------------------
def commitToDB( records ):
  _session.add_all( records )
  _session.commit()

  return None

def formWaveRecord( waveRecord, spectra, buoyNum ):
  waveRecord = associateWithBuoy( waveRecord, buoyNum )
  waveRecord.wavspectra = spectra
  waveRecord.wavspectraid = '1'

  return waveRecord

