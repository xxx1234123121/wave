"""
Overview
--------

This module abstracts the WaveConnect database into a set of
Python classes that can be used by other scripts to interact with
the database.


**Development Status:**
  **Last Modified:** December 13, 2010 by Charlie Sharpsteen

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
#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from warnings import warn, catch_warnings, simplefilter

#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, synonym

from geoalchemy import GeometryColumn, SpatialElement
from geoalchemy import Point


#------------------------------------------------------------------------------
#  Metadata, Object Classes and Other Constants
#------------------------------------------------------------------------------
from wavecon.config import DBconfig as DB_CONFIG
def mkDbURL( DBconfig ):
  url = "{type}://{username}:{password}@{server}/{database}"\
    .format(**DBconfig)

  return url

DB_ENGINE = create_engine(mkDbURL(DB_CONFIG))
# SQLAlchmey whines because it can't figure out what to do with
# GIS columns in the database.  This shuts it up.
DB_META = MetaData(bind=DB_ENGINE)
with catch_warnings():
  simplefilter('ignore')
  DB_META.reflect()

def _tblSourceTypeTmpl( tableName, BaseClass ):

  class SourceType(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 

    def __init__( self, sourceTypeName = None ):
      self.sourcetypename = sourceTypeName

    def __repr__(self):
      return "<SourceTypeRecord('{}')>".format(
        self.sourcetypename )

    id = synonym( 'sourcetypeid' )


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

    id = synonym( 'srcid' )


  return Source


def _tblSpectraBinTmpl( tableName, BaseClass ):

  class SpectraBin(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 

    def __init__( self, spcFreq = None, spcDir = None ):
      self.spcfreq = spcFreq
      self.spcdir = spcDir

    def __repr__(self):
      return "<SpectraBinRecord('{}','{}')>".format(
        self.spcfreq, self.spcdir )

    id = synonym( 'spcid' )

  return SpectraBin


def _tblWaveTmpl( tableName, BaseClass ):

  BaseClass = spatiallyEnable(BaseClass)

  class Wave(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 
    wavlocation = GeometryColumn( Point(2) )

    def __init__( self, wavSourceID = None, wavSpectraBinID = None, 
      wavLocation = None, wavDateTime = None, wavSpectra = None, 
      wavHeight = None, wavPeakDir = None, wavPeakPeriod = None
    ):
      self.wavsourceid = wavSourceID
      self.wavspectrabinid = wavSpectraBinID
      self.wavlocation = wavLocation
      self.wavdatetime = wavDateTime
      self.wavspectra = wavSpectra
      self.wavheight = wavHeight
      self.wavpeakdir = wavPeakDir
      self.wavpeakperiod = wavPeakPeriod

    def __repr__(self):
      return "<SpectraRecord('{}','{}','{}','{}','{}','{}','{}','{}')>"\
        .format( self.wavsourceid, self.wavspectrabinid, self.recoverWKT(),
          self.wavdatetime, self.wavspectra, self.wavheight,
          self.wavpeakdir, self.wavpeakperiod )

    id = synonym( 'wavid' )
    sourceid = synonym( 'wavsourceid' )
    datetime = synonym( 'wavdatetime' )
    location = synonym( 'wavlocation' )


  return Wave


def _tblWindTmpl( tableName, BaseClass ):

  BaseClass = spatiallyEnable(BaseClass)

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
        self.winsourceid, self.recoverWKT(), self.windatetime,
        self.winspeed, self.windirection )

    id = synonym( 'winid' )
    sourceid = synonym( 'winsourceid' )
    datetime = synonym( 'windatetime' )
    location = synonym( 'winlocation' )

  return Wind


def _tblCurrentTmpl( tableName, BaseClass ):

  BaseClass = spatiallyEnable(BaseClass)

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
        self.cursourceid, self.recoverWKT(), self.curdatetime,
        self.curspeed, self.curdirection )

    id = synonym( 'curid' )
    sourceid = synonym( 'cursourceid' )
    datetime = synonym( 'curdatetime' )
    location = synonym( 'curlocation' )

  return Current


def _tblBathyTmpl( tableName, BaseClass ):

  BaseClass = spatiallyEnable(BaseClass)

  class Bathy(BaseClass):
    __tablename__ = tableName
    __table_args__ = {'autoload' : True, 'useexisting' : True } 
    batlocation = GeometryColumn( Point(2) )

    def __init__( self, batSourceID = None, batLocation = None, 
      batDepth = None 
    ):
      self.batsourceid = batSourceID
      self.batlocation = batLocation
      self.batdepth = batDepth

    def __repr__(self):
      return "<BathyRecord('{}','{}','{}')>".format(
        self.batsourceid, self.recoverWKT(), self.batdepth )

    id = synonym( 'batid' )
    sourceid = synonym( 'batsourceid' )
    datetime = synonym( 'batdatetime' )
    location = synonym( 'batlocation' )

  return Bathy


_DATABASE_TEMPLATES = {

  'tblsourcetype' : _tblSourceTypeTmpl,
  'tblsource' : _tblSourceTmpl,
  'tblspectrabin' : _tblSpectraBinTmpl,
  'tblwave' : _tblWaveTmpl,
  'tblwind' : _tblWindTmpl,
  'tblcurrent' : _tblCurrentTmpl,
  'tblbathy' : _tblBathyTmpl

}


#------------------------------------------------------------------
#  Class Utility Methods
#------------------------------------------------------------------
def recordToDict(self):
  """Turns a record pulled from the database into a dictionary.
  In :py:func:`wavecon.DBman.accessTable` this method is attached to
  the Base object from which all classes representing databse objects
  descend.  It provides a convienant way to reduce a database record
  to a basic Python object.

  """
  dictionary = dict( (key, value) for
    key, value in self.__dict__.iteritems()
    if not callable( value ) and not key.startswith('__')
    and not key.startswith('_') 
  )

  locationKeys = [ key
    for key in dictionary.keys()
    if key.endswith('location') ]

  if len(locationKeys):
    Key = locationKeys.pop()
    dictionary[Key] = self.recoverWKT()

  return dictionary

def recoverWKT(self):
  if isinstance(self.location, SpatialElement):
    session = startSession()
    WKT = session.scalar(self.location.wkt)
    session.close()
  elif isinstance(self.location, str):
    WKT = location
  else:
    raise(RuntimeError('''Could not figure out how to recover WKT from an object
    of type {0}'''.format(type(self.location))))

  return WKT

def spatiallyEnable(BaseClass):
  BaseClass.recoverWKT = recoverWKT

  return BaseClass


#------------------------------------------------------------------
#  Database Access Functions
#------------------------------------------------------------------
def accessTable(DBconfig, template, name = None):
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
  if DBconfig is not None:
    warn(FutureWarning('''The DBconfig argument to accessTable will be
    removed soon.'''))

  if name is None:
    name = template

  BaseClass = declarative_base(metadata = DB_META)
  # Add helper methods that will filter to all classes and objects
  # through inheritance.
  BaseClass.recordToDict = recordToDict

  Class = _DATABASE_TEMPLATES[template]( name, BaseClass )

  return Class


def startSession(DBconfig = None):
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
  if DBconfig is not None:
    warn(FutureWarning('''The DBconfig argument to startSession will be
    removed soon.'''))

  session = sessionmaker(bind=DB_ENGINE)()
  return session

