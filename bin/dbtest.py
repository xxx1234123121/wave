from buoyboy import loadDBConfig
cfig = loadDBConfig()
from wavecon import DBman
Wind = DBman.accessDBTable( cfig, 'tblwind' )

#import geoalchemy
import datetime
foo = datetime.datetime.now()
#point = geoalchemy.WKTSpatialElement
win_record = Wind( 1, 1, '(10,10)', foo, 12.0, 42 )
# GAH! ------------^  Shouldn't need the ID!
engine = DBman.connectToDB(cfig)
Session = DBman.sessionmaker(bind=engine)
session = Session()
session.add(win_record)
session.commit()
