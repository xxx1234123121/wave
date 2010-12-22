"""
Overview
--------

This module eases access to common configuration files stored in
$PROJECT_ROOT/config


**Development Status:**
  **Last Modified:** December 22, 2010 by Charlie Sharpsteen

Layout
------

The ``config`` module is currently split into two sections.  One
section contains functions that are used to parse configuration
files.  The second section contains objects that hold configuration
info or the results of parsing particular files in the top-level
``config`` directory.::

  #------------------------------------------------------------------
  #  Configuration File Parsing Functions
  #-----------------------------------------------------------------  

  # Here is an function that reads DBconfig objects.
  def loadDBConfig( aPath ):
    configFile = open( aPath, 'r' )

    DBconfig = json.load( configFile )
    configFile.close()

    return DBconfig

  # More functions go here.

  #------------------------------------------------------------------
  #  Configuration Objects
  #------------------------------------------------------------------

  # Here the previously defined loadDBConfig() function is used to
  # pre-load a specific configuration file.  This preloaded
  # information is now available to other scripts through:
  #
  #   from wavecon.config import DBconfig
  #
  DBconfig = loadDBConfig(path.join( CONFIG_DIR, 'dbconfig.json' ))

  # More preloaded objects go here.

"""
#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from os import path
import json


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from jinja2 import Environment, FileSystemLoader


# Find the top-level config directory
_scriptLocation = path.dirname(path.abspath( __file__ ))
CONFIG_DIR = path.abspath(path.join( _scriptLocation, '..', '..', '..',
  'config' ))
"""``CONFIG_DIR`` holds the path to the top-level ``config`` directory."""

CMS_TEMPLATE_DIR = path.abspath(path.join(_scriptLocation, '..', '..', '..',
  'cms', 'templates'))
"""``CMS_TEMPLATE_DIR`` holds the path to a top-level directory containing
templates for the input files of the CMS model.
"""

#------------------------------------------------------------------
#  Configuration File Parsing Functions
#-----------------------------------------------------------------
def loadDBConfig( aPath ):
  configFile = open( aPath, 'r' )

  DBconfig = json.load( configFile )
  configFile.close()

  return DBconfig


#------------------------------------------------------------------
#  Configuration Objects
#------------------------------------------------------------------
DBconfig = loadDBConfig(path.join( CONFIG_DIR, 'dbconfig.json' ))
"""Configuration information for accessing databases.
Automagically generated from config/dbconfig.json. ``DBconfig`` is
a python dictionary with the following structure::

  {
    "username" : "aUser",
    "password" : "aPassword",
    "database" : "aDB",
    "server" : "localhost",
    "type" : "postgresql"  
  }

Some functions which use this object are: 

  * :py:func:`wavecon.DBman.startSession`
  * :py:func:`wavecon.DBman.accessTable`

"""

#------------------------------------------------------------------
#  CMS Config section
#------------------------------------------------------------------
def loadCMSConfig( aPath ):
  configFile = open( aPath, 'r')
  cmsconfig = json.load( configFile )
  configFile.close()
  return cmsconfig

CMSconfig = loadCMSConfig(path.join(CONFIG_DIR, 'cmsconfig.json'))
"""Configuration information for setting up cms input files. Some 
functions which use this object are:
  
  * :py:func:`wavecon.prepareCMSinput.spatialdomain`
  * :py:func:`wavecon.prepareCMSinput.temporaldomain`
  * :py:func:`wavecon.prepareCMSinput.getwavedata`
  * :py:func:`wavecon.prepareCMSinput.getwinddata`
""" 

CMS_TEMPLATES = Environment(loader=FileSystemLoader(CMS_TEMPLATE_DIR))

