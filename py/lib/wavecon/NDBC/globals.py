from collections import namedtuple

# Custom objects
Location = namedtuple( 'Location', 'lon lat' )

# Buoy Metadata
BUOY_META = {

  '46022' : {
    'location' : Location(-124.577, 40.749),
    'type' : 'NDBC'
  },

  '46212' : {
    'location' : Location(-124.313, 40.753),
    'type' : 'SCRIPPS'
  },

  '46244' : {
    'location' : Location(-124.357, 40.888),
    'type' : 'SCRIPPS'
  }

}
