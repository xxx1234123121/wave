#!/usr/bin/env python

# Make sure the WaveConnect py/lib folder is on the search path so
# modules can be retrieved.
import sys
from os import path, system
scriptLocation = path.dirname(path.abspath(__file__))
waveLibs = path.abspath(path.join(scriptLocation, '..', 'lib'))
sys.path.insert(0, waveLibs)


from wavecon.config import DBconfig
from wavecon import DBman
from wavecon.NDBC.DB import getBuoyID

from datetime import datetime
from geoalchemy import WKTSpatialElement

Wind = DBman.accessTable(DBconfig, 'tblwind', 'tblwind')
session = DBman.startSession(DBconfig)

records = session.query(Wind).all()

if len(records) == 0:
  dbTest = path.abspath(path.join(scriptLocation, 'dbtest.py'))
  system('pythonw {0}'.format(dbTest))
  records = session.query(Wind).all()

record = records[0]

print record
