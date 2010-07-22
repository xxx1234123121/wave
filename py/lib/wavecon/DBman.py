import sqlalchemy
import geoalchemy

from sqlalchemy import Table

"""
-------------------------------------------------------------------
   Python Classes Bound to Database Schema
-------------------------------------------------------------------

Going to try this the "reflective" way- which means SQLAlchemy will
infer the layout of the database tables by talking to the database.
Some special columns, such as GIS Points, will have to be declared
manually using GeoAlchemy extensions.

The advantage to this aproach is that it is quick n' dirty to
implement.

The drawbacks are that the database structure is very opaque to the
Python programmer- most everything is happening by "magic".  Also,
the bython classes which are bound to the database tables *must*
have attributes whose names match the names of the columns.

If it becomes a maintainence nightmare, the alternative is to switch
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

-------------------------------------------------------------------
"""
class Wind(Base):




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
