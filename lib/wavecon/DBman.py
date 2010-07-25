"""
Overview
--------

This module abstracts the WaveConnect database into a set of
Python classes that can be used by other scripts to interact with
the database.


**Development Status:**
  **Last Modified:** July 24, 2010 by Charlie Sharpsteen

"Design Notes"/Ravings
----------------------

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
from sqlalchemy.orm import sessionmaker, synonym

from geoalchemy import GeometryColumn
from geoalchemy import Point

import warnings


def _tblSourceTypeTmpl( tableName, BaseClass ):

  class SourceType(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 

    def __init__( self, sourceTypeName = None ):
      self.sourcetypename = sourceTypeName

    def __repr__(self):
      return "<SourceTypeRecord('{}')>".format(
        self.sourcetypename )


  return SourceType


def _tblSourceTmpl( tableName, BaseClass ):

  class Source(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 

    def __init__( self, srcName = None, srcConfig = None, 
      srcBeginExecution = None , srcEndExecution = None, 
      srcSourceTypeID = None 
    ):
      self.srcname = srcName
      self.srcconfig = srcConfig
      self.srcbeginexecution = srcBeginExecution
      self.srcendexecution = srcEndExecution
      self.srcsourcetypeid = srcSourceTypeID

    def __repr__(self):
      return "<SourceRecord('{}','{}','{}','{}','{}')>".format(
        self.srcname, self.srcconfig, self.srcbeginexecution,
        self.srcendexecution, self.srcsourcetypeid )

    srcid = synonym( 'id', map_column = True )


  return Source


def _tblSpectraTmpl( tableName, BaseClass ):

  class Spectra(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 

    def __init__( self, spectraFreq = None, spectraDir = None ):
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

    def __init__( self, wavSourceID = None, wavSpectraID = None, 
      wavLocation = None, wavDateTime = None, wavSpectra = None, 
      waveHeight = None, wavPeakDir = None, wavPeakPeriod = None
    ):
      self.wavsourceid = wavSourceID
      self.wavspectraid = wavSpectraID
      self.wavlocation = wavLocation
      self.wavdatetime = wavDateTime
      self.wavspectra = wavSpectra
      self.wavheight = wavHeight
      self.wavpeakdir = wavPeakDir
      self.wavpeakperiod = wavPeakPeriod

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

    def __init__( self, winSourceID = None, winLocation = None, 
      winDateTime = None, winSpeed = None, winDirection = None
    ):
      self.winsourceid = winSourceID
      self.winlocation = winLocation
      self.windatetime = winDateTime
      self.winspeed = winSpeed
      self.windirection = winDirection

    def __repr__(self):
      return "<WindRecord('{}','{}','{}','{}','{}')>".format(
        self.winsourceid, self.winlocation, self.windatetime,
        self.winspeed, self.windirection )

    winid = synonym( 'id', map_column = True )
    winsourceid = synonym( 'sourceid', map_column = True )
    windatetime = synonym( 'datetime', map_column = True )
    winlocation = synonym( 'location', map_column = True )

  return Wind


def _tblCurrentTmpl( tableName, BaseClass ):

  class Current(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 
    curlocation = GeometryColumn( Point(2) )

    def __init__( self, curSourceID = None, curLocation = None, 
      curDateTime = None, curSpeed = None, curDirection = None 
    ):
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

    def __init__( self, bathySourceID = None, bathyLocation = None, 
      bathyDepth = None 
    ):
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
#  Class Utility Methods
#------------------------------------------------------------------
def recordToDict( object ):
  """Turns a record pulled from the database into a dictionary.
  In :py:func:`wavecon.DBman.accessTable` this method is attached to
  the Base object from which all classes representing databse objects
  descend.  It provides a convienant way to reduce a database record
  to a basic Python object.

  """
  dictionary = dict( (key, value) for
    key, value in object.__dict__.iteritems()
    if not callable( value ) and not key.startswith('__')
    and not key.startswith('_') 
  )

  return dictionary


#------------------------------------------------------------------
#  Database Access Functions
#------------------------------------------------------------------
def accessTable( DBconfig, template, name = None ):
  """Returns a Class that can be used to spawn objects which are 
  suitable for serialization to a database table.

  Argument Info:

    * *DBconfig*:
        A python dictionary containing access credentials for the
        database server.  See :py:data:`wavecon.config.DBconfig`
        for the structure of this dictionary.

    * *template*
        A string specifying the Schema that should be used to model
        the database table you are trying to access.  I.E. if you
        are trying to access a table that is defined like
        ``tblWave`` in ``DB.psql`` then pass the string
        ``'tblwave'``

    * *name*
        An optional name for the database table. I.E. you are
        trying to access a table that has the same schema as
        ``tblWave`` but is called ``tblWaveModeled``.  You would
        then pass ``'tblwave'`` for the *template* parameter and
        ``'tblwavemodeled'`` for the *name* parameter.  If left
        blank it will default to the value passed for *template*

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
    # Add helper methods that will filter to all classes and objects
    # through inheritance.
    BaseClass.recordToDict = recordToDict
  
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

  See :py:data:`wavecon.config.DBconfig` for a description of the
  *DBconfig* parameter.

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
