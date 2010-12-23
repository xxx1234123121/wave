import json
from datetime import datetime
from types import GeneratorType
from itertools import chain
from numpy import ndarray

class RecordEncoder(json.JSONEncoder):
  def default( self, obj ):
    if isinstance( obj, datetime ):
      return obj.isoformat()
    elif isinstance(obj, ndarray):
      return obj.tolist()
    elif isinstance(obj, GeneratorType) or isinstance(obj, chain):
      return list(obj)
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
