from collections import namedtuple

# Custom objects
Location = namedtuple( 'Location', 'lon lat' )

# Buoy Metadata
BUOY_META = {

  '46022' : {
    'location' : Location( 40.749, -124.577 ),
    'type' : 'NDBC'
  },

  '46212' : {
    'location' : Location( 40.753, -124.313 ),
    'type' : 'SCRIPPS'
  },

  '46244' : {
    'location' : Location( 40.888, -124.357 ),
    'type' : 'SCRIPPS'
  }

}
