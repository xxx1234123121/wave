"""
Overview
--------

This module provides routines for serializing CMS data module to a SQL database.

(Currently, use of the ARRAY and DOUBLE_PRECISION functions limits this to use
with PostgreSQL databases.)

**Development Status:**
  **Last Modified:** December, 17 2010 by Charlie Sharpsteen
"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from uuid import uuid4

#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from sqlalchemy import and_
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
SourceTypeRecord = DBman.accessTable(None, 'tblsourcetype')
Source = DBman.accessTable(None, 'tblsource')
CurrentRecord = DBman.accessTable(None, 'tblcurrent')
WaveRecord = DBman.accessTable(None, 'tblwave')
SpectraRecord = DBman.accessTable(None, 'tblspectrabin' )

_session = DBman.startSession()


#------------------------------------------------------------------------------
#  Forming and Committing Database Records
#------------------------------------------------------------------------------
def CurrentDBrecordGenerator(current_data, model_run_id):

  records = (
    {
      'curid': uuid4(),
      'cursourceid': model_run_id,
      'curdatetime': record['timestamp'],
      'curspeed': record['speed'],
      'curdirection': record['direction'],
      'curlocation': 'SRID=4326;POINT({0} {1})'.format(*record['location'])
    }
    for record in current_data
  )

  return records


#------------------------------------------------------------------------------
#  Database SourceType Representation
#------------------------------------------------------------------------------
def getSourceTypeID(sourceName):
  sourceType = _session.query(SourceTypeRecord).filter( 
    SourceTypeRecord.sourcetypename == sourceName
  ).first()

  if sourceType:
    return sourceType.id
  else:
    # A record for this source type does not exist in the DB. Create it.
    sourceType = SourceTypeRecord(sourceTypeName = sourceName)

    _session.add(sourceType)
    _session.commit()

    return sourceType.id


#------------------------------------------------------------------------------
#  Database Model Run Representation
#------------------------------------------------------------------------------
def getModelRunID(run_info):
  model_run = _session.query(Source).filter(and_(
    Source.srcname == run_info['run_name'],
    Source.srcbeginexecution == run_info['start_time'],
    Source.srcendexecution == run_info['stop_time'] 
  )).first()

  if model_run:
    return model_run.id
  else:
    # Create a record for the model run.
    model_run = Source(srcName = run_info['run_name'],
      srcBeginExecution = run_info['start_time'],
      srcEndExecution = run_info['stop_time'],
      srcSourceTypeID = getSourceTypeID('Model-CMS')
    )

    _session.add(model_run)
    _session.commit()

    return model_run.id


#---------------------------------------------------------------------
#  Database Interaction
#---------------------------------------------------------------------
def commitToDB(records):
  _session.add_all(records)
  _session.commit()

  return None

