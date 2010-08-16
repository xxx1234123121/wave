"""
Overview
--------

This module provides routines for serializing data obtained by the data.py
module to a SQL database.

**Development Status:**
  **Last Modified:** August 16, 2010 by Charlie Sharpsteen


"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------

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
WindRecord = DBman.accessTable( _DBconfig, 'tblwind' )
WaveRecord = DBman.accessTable( _DBconfig, 'tblwave' )

_session = DBman.startSession( _DBconfig )


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

def formWaveRecord( waveRecord, spectra, buoyNum ):
  waveRecord = associateWithBuoy( waveRecord, buoyNum )
  waveRecord.wavspectra = spectra
  waveRecord.wavspectraid = '1'

  return waveRecord

def commitToDB( records ):
  _session.add_all( records )
  _session.commit()

  return None
