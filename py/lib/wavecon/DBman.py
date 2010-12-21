"""
Overview
--------

This module abstracts the WaveConnect database into a set of Python classes that
simplifies database interaction for scripts and other modules in this software
collection.

**Development Status:**
  **Last Modified:** December 20, 2010 by Charlie Sharpsteen


Implementation Details
----------------------
The DBman module implements an interface to a `PostGIS`_ database by leveraging
the `SQLAlchemy`_ module and the `GeoAlchemy`_ extension to that module.

SQLAlchemy implements an Object Relational Mapper (ORM) that allows Python classes
to be bound to database records.  The data contained in these objects may be
committed to the database as records and the results of database queries are
automatically transformed into database objects.

Most of the code implemented in the module is database-agnostic.  However, there
is a tiny bit of code that relies on the Postgresql implementation of an `ARRAY
datatype`_.  Consequently, this module is only recommended for use with
Postgresql and PostGIS.


.. _PostGIS: http://postgis.refractions.net/
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _GeoAlchemy: http://www.sqlalchemy.org/
.. _ARRAY datatype: http://www.postgresql.org/docs/9.0/interactive/arrays.html
"""
#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from warnings import warn, catch_warnings, simplefilter
import random
from string import ascii_lowercase
import csv
import tempfile
import os

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
from config import DBconfig as DB_CONFIG
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


#------------------------------------------------------------------------------
#  Database Schema
#------------------------------------------------------------------------------
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
  """For records that contain a spatial component, this function will return the
  coordinates of that component as a string of `Well Known Text`_ (WKT).

  .. _Well Known Text: http://en.wikipedia.org/wiki/Well-known_text
  """
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
        .. deprecated:: 12-2010
           This argument is depreciated and is slated for removal

           A python dictionary containing access credentials for the database
           server.  See :py:data:`wavecon.config.DBconfig` for the structure of
           this dictionary.

           Currently ignored due to depreciated status.

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

    * `SQLAlchemy documentation`_.  Describes basic usage.

    * `GeoAlchemy documentation`_.  Describes how to run PostGIS
      enabled queries.

  .. deprecated:: 12-2010
     The DBconfig argument is depreciated and is slated for removal


  .. _SQLAlchemy documentation: http://www.sqlalchemy.org/docs/ormtutorial.html#
       creating-a-session
  .. _GeoAlchemy documentation: http://www.geoalchemy.org/tutorial.html#
       performing-spatial-queries
  """
  if DBconfig is not None:
    warn(FutureWarning('''The DBconfig argument to startSession will be
    removed soon.'''))

  session = sessionmaker(bind=DB_ENGINE)()
  return session


def RawPostgresConnection(config = DB_CONFIG):
  # Isolated imports so DBman does not crash when imported to connect to a
  # non-Postgres database.  Currently not ever done or supported, but hey, who
  # knows what the future will hold?
  from psycopg2 import connect

  return connect('dbname={database} user={username} password={password}'.\
    format(**config))


def bulk_import(records, table_template, table_name = None):
  """Efficient loading of large datasets into PostgreSQL
  
  .. note:: This function will only work with PostgreSQL databases

  Argument Info:

    * *records*:
        A list of python dictionaries whose key/value pairs correspond to the
        names and datatypes of the PostgreSQL table that is to receive the data.

        For large datasets, a generator that can produce the list one element at
        a time should be used so that Python does not allocate large amounts of
        RAM to store a temporary variable.  This saves resources for Postgres.

    * *table_template*
        A string specifying the Schema that should be used to model the database
        into which data is to be loaded.  I.E. if trying to load data into a
        table that is defined like ``tblWave`` in ``DB.psql`` then pass the
        string ``'tblwave'``

    * *table_name*
        An optional name for the database table. I.E. if loading data into a
        table that has the same schema as ``tblWave`` but is called
        ``tblWaveModeled``, pass ``'tblwave'`` for the *table_template*
        parameter and ``'tblwavemodeled'`` for the *table_name* parameter.  If
        left blank this will default to the value passed for *table_template*

  .. todo::
     Currently this function dumps the records to a temporary CSV file and
     then uses the Postgresql ``COPY`` to load the data from CSV.  The time it
     takes this function to execute can be cut by approximately 33% if the
     temporary CSV file could be eliminated.
  """

  if table_name is None:
    table_name = table_template

  # Dump records to temporary CSV file
  #========================================================================
  # Retrieve order of table column names
  table = accessTable(None, table_template, table_name)
  table_columns = table.__table__._columns.keys()

  temp_file = tempfile.mkstemp()
  os.close(temp_file[0]) # Just wanted the path, thank you
  temp_file = temp_file[1]

  # Open file in binary mode because the table columns are returned as UTF-8
  # strings and writing UTF-8 to non-binary files results in bad output for some
  # reason.
  csv_file = open(temp_file, 'wb')
  csv_writer = csv.DictWriter(csv_file, fieldnames = table_columns)

  # Loop over each record and commit individually with `writerow()` rather than
  # all at once with `writerows()` as records should be a generator and this
  # prevents the entire dataset from being expanded in memory.
  #
  # TODO: Add an isinstance() check for generators or lists and use the most
  # efficient method for each.
  for record in records:
    csv_writer.writerow(record)

  csv_file.close()

  # Import records into database
  #========================================================================
  # Create a name for the temporary table padded with some random ASCII
  # characters in case multiple bulk imports are running at the same time.
  temp_table = 'bulk_import_' + \
    ''.join((random.choice(ascii_lowercase) for i in xrange(4)))

  # Open a raw database connection using psycopg2.  Stand by for some low-level
  # voodoo.
  connection = RawPostgresConnection()
  cursor = connection.cursor()

  cursor.execute('''
    CREATE TEMP TABLE {temp_table} ( LIKE {target_table} );
    '''.format(
      temp_table = temp_table,
      target_table = table_name,
    )
  )

  csv_file = open(temp_file,'r')
  cursor.copy_from(csv_file, temp_table, sep = ',', null = '')
  csv_file.close()

  cursor.execute('''
    INSERT INTO {target_table} SELECT * FROM {temp_table};
    DROP TABLE {temp_table};
    '''.format(
      temp_table = temp_table,
      target_table = table_name,
    )
  )

  connection.commit()

  cursor.close()
  connection.close()
  os.unlink(temp_file)

  return None

