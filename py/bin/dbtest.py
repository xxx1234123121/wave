#!/usr/bin/env python
from buoyboy import loadDBConfig
cfg = loadDBConfig()

from wavecon import DBman
session = DBman.startSession( cfg )

from datetime import datetime

Wind = DBman.accessTable( cfg, 'tblwind', 'tblwind' )

windTest = Wind( '1', 'POINT(40.86 -124.08)', datetime.now(), 12.0, 120.0 )
print windTest

session.add(windTest)
session.commit()

for record in session.query(Wind):
  print session.scalar(record.winlocation.wkt)
