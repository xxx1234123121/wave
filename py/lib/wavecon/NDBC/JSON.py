import json
from datetime import datetime
from numpy import ndarray

class BuoyRecordEncoder(json.JSONEncoder):
  def default( self, obj ):
    if isinstance( obj, datetime ):
      return obj.isoformat()
    if isinstance( obj, ndarray ):
      return obj.tolist()
    else:
      return json.JSONEncoder.default( self, obj )

def writeJSON( NDBCrecords, fileHandle ):
  fileHandle.write(json.dumps(
    NDBCrecords,
    indent = 2,
    cls = BuoyRecordEncoder
  ))

  return None

def clobber( object ):
  return json.loads(json.dumps(
    object,
    cls = DatetimeEncoder
  ))
