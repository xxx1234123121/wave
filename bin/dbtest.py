#!/usr/bin/env python

# Make sure the WaveConnect py/lib folder is on the search path so
# modules can be retrieved.
import sys
from os import path
scriptLocation = path.dirname(path.abspath( __file__ ))
waveLibs = path.abspath(path.join( scriptLocation, '..', 'lib' ))
sys.path.insert( 0, waveLibs )


from wavecon.config import DBconfig
from wavecon import DBman

from datetime import datetime

Wind = DBman.accessTable( DBconfig, 'tblwind', 'tblwind' )
session = DBman.startSession( DBconfig )

windTest = Wind( '1', 'POINT(40.86 -124.08)', datetime.now(), 12.0, 120.0 )
print windTest

session.add(windTest)
session.commit()

for record in session.query(Wind):
  print session.scalar(record.winlocation.wkt)
