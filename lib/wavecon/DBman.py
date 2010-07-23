"""
-------------------------------------------------------------------
This module abstracts the WaveConnect database into a set of Python
classes that can be used by other scripts to interact with the
database.

Version:       0.1.0
Author:        Charlie Sharpsteen <source@sharpsteen.net>
Last Modified: July 23, 2010 by Charlie Sharpsteen
-------------------------------------------------------------------
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table
from sqlalchemy.orm import mapper, sessionmaker

from geoalchemy import GeometryExtensionColumn, GeometryColumn
from geoalchemy import Point
from geoalchemy import GeometryDDL
from geoalchemy.postgis import PGComparator

import warnings

"""
-------------------------------------------------------------------
   Python Classes Bound to Database Schema
-------------------------------------------------------------------

Going to try this the "reflective" way- which means SQLAlchemy will
infer the layout of the database tables by talking to the database.
Some special columns, such as GIS Points, will have to be declared
manually using GeoAlchemy extensions.

The advantage to this approach is that it is quick n' dirty to
implement.

The drawbacks are that the database structure is very opaque to the
Python programmer- most everything is happening by "magic".  Also,
the Python classes which are bound to the database tables *must*
have attributes whose names match the names of the columns.

If it becomes a maintenance nightmare, the alternative is to switch
to a "declarative" style as described in:

  http://www.sqlalchemy.org/docs/ormtutorial.html#
    creating-table-class-and-mapper-all-at-once-declaratively

With the declarative style, the database Table schema is embedded
inside the Python classes that are being mapped to those tables.

The good news is that we can switch from "reflective" to 
"declarative" without changing how use the Python objects that are
being mapped to database tables. I.E. other scripts that depend
on this module will not have to be re-written because the DBman API
will not change.

-------------------------------------------------------------------

Update:

  After implementing the reflective style, I feel it has one nice
  advantage over the declarative style for our use case.  With the
  reflective style, one does not have to worry about managing 
  things such as ForeignKeys or Constraints or Indexes or...

  So, as long as our Schema is defined in a SQL script, this is the
  way to go.

-------------------------------------------------------------------
"""
def tblSourceTypeTmpl( tableName, metaData ):

  class SourceType(object):
    def __init__( self, sourceTypeName ):
      self.sourcetypename = sourceTypeName

    def __repr__(self):
      return "<SourceTypeRecord('{}')>".format(
        self.sourcetypename )


  table = Table( tableName, metaData,
    autoload = True, useexisting = True )

  mapper( SourceType, table)

  return SourceType


def tblSourceTmpl( tableName, metaData ):

  class Source(object):
    def __init__( self, srcName, srcConfig, srcBeginExecution,
      srcEndExecution, srcSourceTypeID ):
      self.srcname = srcname
      self.srcconfig = srcconfig
      self.srcbeginexecution = srcbeginexecution
      self.srcendexecution = srcendexecution
      self.srcsourcetypeid = srcsourcetypeid

    def __repr__(self):
      return "<SourceRecord('{}','{}','{}','{}','{}')>".format(
        self.srcname, self.srcconfig, self.srcbeginexecution,
        self.srcendexecution, self.srcsourcetypeid )


  table = Table( tableName, metaData,
    autoload = True, useexisting = True )

  mapper( Source, table)

  return Source


def tblSpectraTmpl( tableName, metaData ):

  class Spectra(object):
    def __init__( self, spectraFreq, spectraDir ):
      self.spectrafreq = spectraFreq
      self.spectradir = spectraDir

    def __repr__(self):
      return "<SpectraRecord('{}','{}')>".format(
        self.spectrafreq, self.spectradir )


  table = Table( tableName, metaData,
    autoload = True, useexisting = True )

  mapper( Spectra, table)

  return Spectra


def tblWaveTmpl( tableName, metaData ):

  class Wave(object):
    def __init__( self, wavSourceID, wavSpectraID, wavLocation,
      wavDateTime, wavSpectra, waveHeight, wavPeakDir, wavPeakPeriod ):
      self.wavsourceid = wavSourceID
      self.wavspectraid = wavSpectraID
      self.wavlocation = wavLocation
      self.wavdatetime = wavDateTime
      self.wavspectra = wavspectra
      self.wavheight = wavheight
      self.wavpeakdir = wavpeakdir
      self.wavpeakperiod = wavpeakperiod

    def __repr__(self):
      return "<SpectraRecord('{}','{}','{}','{}','{}','{}','{}','{}')>"\
        .format( self.wavsourceid, self.wavspectraid, self.wavlocation,
          self.wavdatetime, self.wavspectra, self.wavheight,
          self.wavpeakdir, self.wavpeakperiod )


  table = Table( tableName, metaData,
    GeometryExtensionColumn( 'wavlocation', Point(2) ),
    autoload = True, useexisting = True )

  mapper( Wind, table, properties = {
    'wavlocation' : GeometryColumn( table.c.wavlocation )
  })

  return Wave


def tblWindTmpl( tableName, metaData ):

  class Wind(object):
    def __init__( self, winSourceID, winLocation, winDateTime,
      winSpeed, winDirection ):
      self.winsourceid = winSourceID
      self.winlocation = winLocation
      self.windatetime = winDateTime
      self.winspeed = winSpeed
      self.windirection = winDirection

    def __repr__(self):
      return "<WindRecord('{}','{}','{}','{}','{}')>".format(
        self.winsourceid, self.winlocation, self.windatetime,
        self.winspeed, self.windirection )


  table = Table( tableName, metaData,
    GeometryExtensionColumn( 'winlocation', Point(2)),
    autoload = True, useexisting = True )

  mapper( Wind, table, properties = {
    'winlocation' : GeometryColumn( table.c.winlocation,
      comparator = PGComparator )
  })

  GeometryDDL( table )

  return Wind


def tblCurrentTmpl( tableName, metaData ):

  class Current(object):
    def __init__( self, curSourceID, curLocation, curDateTime,
      curSpeed, curDirection ):
      self.cursourceid = curSourceID
      self.curlocation = curLocation
      self.curdatetime = curDateTime
      self.curspeed = curSpeed
      self.curdirection = curDirection

    def __repr__(self):
      return "<CurrentRecord('{}','{}','{}','{}','{}')>".format(
        self.cursourceid, self.curlocation, self.curdatetime,
        self.curspeed, self.curdirection )


  table = Table( tableName, metaData,
    GeometryExtensionColumn( 'curlocation', Point(2) ),
    autoload = True, useexisting = True )

  mapper( Current, table, properties = {
    'curlocation' : GeometryColumn( table.c.curlocation )
  })

  GeometryDDL( table )

  return Current


def tblBathyTmpl( tableName, metaData ):

  class Bathy(object):
    def __init__( self, bathySourceID, bathyLocation, bathyDepth ):
      self.bathysourceid = bathySourceID
      self.bathylocation = bathyLocation
      self.bathydepth = bathyDepth

    def __repr__(self):
      return "<BathyRecord('{}','{}','{}')>".format(
        self.bathysourceid, self.bathylocation, self.bathydepth )


  table = Table( tableName, metaData,
    GeometryExtensionColumn( 'curlocation', Point(2) ),
    autoload = True, useexisting = True )

  mapper( Bathy, table, properties = {
    'bathylocation' : GeometryColumn( table.c.bathylocation )
  })

  GeometryDDL( table )

  return Bathy


DATABASE_TEMPLATES = {

  'tblsourcetype' : tblSourceTypeTmpl,
  'tblsource' : tblSourceTmpl,
  'tblspectra' : tblSpectraTmpl,
  'tblwave' : tblWaveTmpl,
  'tblwind' : tblWindTmpl,
  'tblcurrent' : tblCurrentTmpl,
  'tblbathy' : tblBathyTmpl

}


"""
-------------------------------------------------------------------
   Database Access Functions
-------------------------------------------------------------------
"""
def accessTable( DBconfig, template, name = None ):
  if name is None:
    name = template
  # SQLAlchmey whines because it can't figure out what to do with
  # GIS columns in the database.  This shuts it up.
  with warnings.catch_warnings():
    warnings.simplefilter('ignore')

    engine = connectTo( DBconfig )

    meta = MetaData( bind = engine )
    meta.reflect()
  
    Class = DATABASE_TEMPLATES[template]( name, meta )

    return Class

def startSession( DBconfig ):
  engine = connectTo( DBconfig )
  Session = sessionmaker( bind = engine )

  return Session()


def connectTo( DBconfig ):
  url = "{type}://{username}:{password}@{server}/{database}"\
    .format(**DBconfig)

  engine = create_engine( url )
  return engine
