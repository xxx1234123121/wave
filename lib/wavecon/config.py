"""
-------------------------------------------------------------------
This module eases access to common configuration files stored in
$PROJECT_ROOT/config

Version:       0.1.0
Author:        Charlie Sharpsteen <source@sharpsteen.net>
Last Modified: July 23, 2010 by Charlie Sharpsteen
-------------------------------------------------------------------
"""
from os import path
import json

# Find the top-level config directory
_scriptLocation = path.dirname(path.abspath( __file__ ))
CONFIG_DIR = path.abspath(path.join( _scriptLocation, '..', '..', '..',
  'config' ))


"""
-------------------------------------------------------------------
   Configuration File Parsing Functions
-------------------------------------------------------------------
"""
def loadDBConfig( aPath ):
  configFile = open( aPath, 'r' )

  DBconfig = json.load( configFile )
  return DBconfig


"""
-------------------------------------------------------------------
   Configuration Objects
-------------------------------------------------------------------
"""
DBconfig = loadDBConfig(path.join( CONFIG_DIR, 'dbconfig.json' ))
