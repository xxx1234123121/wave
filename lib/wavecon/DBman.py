import sqlalchemy
import geoalchemy

"""
-------------------------------------------------------------------
   Database Access Functions
-------------------------------------------------------------------
"""
def getDBTable( DBconfig, name ):
  engine = connectDB( DBconfig )

  meta = sqlalchemy.MetaData( bind = engine )

  table = sqlalchemy.Table( name, meta,
      autoload = True )

  return table


def connectDB( DBconfig ):
  url = "{type}://{username}:{password}@{server}/{database}"\
    .format(**DBconfig)

  engine = sqlalchemy.create_engine( url )
  return engine
