"""
Overview
--------

This module abstracts the WaveConnect database into a set of
Python classes that can be used by other scripts to interact with
the database.


.. admonition:: Development Status


  **Last Modified:** July 23, 2010 by Charlie Sharpsteen

Ravings or "Design Notes"
-------------------------

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

.. note:: Update

  After implementing the reflective style, I feel it has one nice
  advantage over the declarative style for our use case.  With the
  reflective style, one does not have to worry about managing 
  things such as Foreign Keys or Constraints or Indexes or...

  So, as long as our Schema is defined in a SQL script, this is the
  way to go.

.. note:: Update to update:

  I stumbled across an example in the GeoAlchemy source code that
  shows how to combine the reflexive and declarative styles.  This
  should give the best of both worlds and reduce the verbosity and
  repetition of the code by a significant amount.

"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from geoalchemy import GeometryColumn
from geoalchemy import Point

import warnings


def _tblSourceTypeTmpl( tableName, BaseClass ):

  class SourceType(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 

    def __init__( self, sourceTypeName ):
      self.sourcetypename = sourceTypeName

    def __repr__(self):
      return "<SourceTypeRecord('{}')>".format(
        self.sourcetypename )


  return SourceType


def _tblSourceTmpl( tableName, BaseClass ):

  class Source(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 

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


  return Source


def _tblSpectraTmpl( tableName, BaseClass ):

  class Spectra(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 

    def __init__( self, spectraFreq, spectraDir ):
      self.spectrafreq = spectraFreq
      self.spectradir = spectraDir

    def __repr__(self):
      return "<SpectraRecord('{}','{}')>".format(
        self.spectrafreq, self.spectradir )


  return Spectra


def _tblWaveTmpl( tableName, BaseClass ):

  class Wave(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 
    wavlocation = GeometryColumn( Point(2) )

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


  return Wave


def _tblWindTmpl( tableName, BaseClass ):

  class Wind(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 
    winlocation = GeometryColumn( Point(2) )

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


  return Wind


def _tblCurrentTmpl( tableName, BaseClass ):

  class Current(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 
    curlocation = GeometryColumn( Point(2) )

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


  return Current


def _tblBathyTmpl( tableName, BaseClass ):

  class Bathy(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 
    bathylocation = GeometryColumn( Point(2) )

    def __init__( self, bathySourceID, bathyLocation, bathyDepth ):
      self.bathysourceid = bathySourceID
      self.bathylocation = bathyLocation
      self.bathydepth = bathyDepth

    def __repr__(self):
      return "<BathyRecord('{}','{}','{}')>".format(
        self.bathysourceid, self.bathylocation, self.bathydepth )


  return Bathy


_DATABASE_TEMPLATES = {

  'tblsourcetype' : _tblSourceTypeTmpl,
  'tblsource' : _tblSourceTmpl,
  'tblspectra' : _tblSpectraTmpl,
  'tblwave' : _tblWaveTmpl,
  'tblwind' : _tblWindTmpl,
  'tblcurrent' : _tblCurrentTmpl,
  'tblbathy' : _tblBathyTmpl

}


#------------------------------------------------------------------
#  Database Access Functions
#------------------------------------------------------------------
def accessTable( DBconfig, template, name = None ):
  """Returns a Class that can be used to spawn objects which are 
  suitable for serialization to a database table.

  """

  if name is None:
    name = template

  # SQLAlchmey whines because it can't figure out what to do with
  # GIS columns in the database.  This shuts it up.
  with warnings.catch_warnings():
    warnings.simplefilter('ignore')

    engine = connectTo( DBconfig )

    meta = MetaData( bind = engine )
    meta.reflect()

    BaseClass = declarative_base( metadata = meta )
  
    Class = _DATABASE_TEMPLATES[template]( name, BaseClass )

    return Class

def startSession( DBconfig ):
  """Returns an object representing a connection to the database.
  This object may be used in combination with a class returned
  by ``accessTable()`` to add objects to the database, run queries,
  perform updates and do all kinds of useful things.

  The following websites explain how to use ``session`` objects:

    * `SQLAlchemy`_ documentation.  Describes basic usage.

    * `GeoAlchemy`_ documentation.  Describes how to run PostGIS
      enabled queries.

    .. _SQLAlchemy: http://www.sqlalchemy.org/docs/ormtutorial.html#
         creating-a-session

    .. _GeoAlchemy: http://www.geoalchemy.org/tutorial.html#
         performing-spatial-queries

  """
  engine = connectTo( DBconfig )
  Session = sessionmaker( bind = engine )

  return Session()


def connectTo( DBconfig ):
  url = "{type}://{username}:{password}@{server}/{database}"\
    .format(**DBconfig)

  engine = create_engine( url )
  return engine
