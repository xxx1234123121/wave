import json
from datetime import datetime

class RecordEncoder(json.JSONEncoder):
  def default( self, obj ):
    if isinstance( obj, datetime ):
      return obj.isoformat()
    else:
      return json.JSONEncoder.default( self, obj )

def writeJSON( records, fileHandle ):
  fileHandle.write(json.dumps(
    records,
    indent = 2,
    cls = RecordEncoder
  ))

  return None

def clobber( object ):
  return json.loads(json.dumps(
    object,
    cls = RecordEncoder
  ))
