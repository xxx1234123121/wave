"""
Overview
--------

This module provides functions for interacting with CMS grid files.
Currently, it contains a parser for reading CMS-Flow telescoping grids.

**Development Status:**
  **Last Modified:** December 17, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
import re
from math import cos, sin, radians


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from numpy import array, dot, transpose
from pyproj import Proj, transform


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  CMS-Flow .tel file parser
#------------------------------------------------------------------------------
def telfile_parser(file_path):
  # NOTE: This routine is returning the locations of the Lower Left corner of
  # each cell.  However, CMS computes values on a cell basis, not a nodal basis.
  # So it would probably be better to extend this routine so that it returns the
  # location of the middle of each cell.
  tel_file = open(file_path, 'r')
  tel_data = tel_file.read().splitlines()

  tel_file.close()

  # Remove first two lines from tel file.  The first line contains a label, the
  # second line contains information duplicated in grid_info.
  tel_data.pop(0); tel_data.pop(0)

  grid_coords = array([ 
    [float(x), float(y)] for x, y in
    [re.split('\s+', line)[1:3] for line in tel_data]
  ])

  return grid_coords


#---------------------------------------------------------------------
#  Utility Functions
#---------------------------------------------------------------------
def georeference_grid(grid_coords, grid_info):
  angle = grid_info['grid_angle']

  # Angles are negative because CMS works with 'compass degrees' which are
  # positive in the clockwise direction while mathematical degrees are positive
  # in the counterclockwise direction.
  rot_matrix = array([
    [cos(radians(-angle)), -sin(radians(-angle))],
    [sin(radians(-angle)), cos(radians(-angle))]
  ])

  grid_coords = dot(rot_matrix, transpose(grid_coords))

  # Set up projection from grid coordinate system to WGS84 lat/lons.
  grid_proj = Proj(init = grid_info['grid_epsg_code'])
  wgs84 = Proj(init = 'EPSG:4326')

  grid_origin = grid_info['grid_origin']
  lons, lats = transform(grid_proj, wgs84,
    grid_coords[0,:] + grid_origin[0],
    grid_coords[1,:] + grid_origin[1] )

  return zip(lons, lats)

