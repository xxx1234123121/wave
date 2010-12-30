"""
Overview
--------

This module provides functions for interacting with CMS grid files.
Currently, it contains a parser for reading CMS-Flow telescoping grids.

**Development Status:**
  **Last Modified:** December 21, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
import re
from string import lstrip
from itertools import chain
from math import cos, sin, radians


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from numpy import array, dot, transpose, cumsum, meshgrid
from pyproj import Proj, transform


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  CMS-Flow .tel file parser
#------------------------------------------------------------------------------
def telfile_parser(file_path):
  # NOTE: This routine is returning the locations of the Lower Left corner of
  # each cell.  However, CMS computes values on a cell-centered basis, not a
  # grid-centered basis.  So, this routine needs to be extended that it returns
  # the location of the middle of each cell.
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


#------------------------------------------------------------------------------
#  CMS-Wave .dep file parser
#------------------------------------------------------------------------------
def depfile_parser(file_path):
  dep_file = open(file_path, 'r')
  dep_data = dep_file.read().splitlines()

  dep_file.close()

  # Remove first line and process it.
  dep_header = dep_data.pop(0)
  ni, nj, dx, dindex = [
    (int(ni), int(nj), float(dx), float(dindex))
    for ni,nj,dx,dindex in [re.split('\s+', dep_header)]
  ][0]

  # Process the rest of the file.
  dep_data = array(list(chain.from_iterable(
    (
      (float(z) for z in re.split('\s+', lstrip(row)))
      for row in dep_data
    )
  )))

  # Determine grid layout based on the value of dindex:
  if dindex == 0:
    # Constant width grid, dy = dx
    dx_vals = [dx] * ni
    dy_vals = [dx] * nj
  elif dindex != 999:
    # Constant width grid with dx = dx and dy = dindex
    dx_vals = [dx] * ni
    dy_vals = [dindex] * nj
  else:
    # Variable width grid, last ni+nj values in dep_data hold the dx and dy
    # values for each cell.
    dx_vals = dep_data[(ni*nj):(ni*nj+ni)]
    dy_vals = dep_data[(ni*nj+ni):]
    dep_data = dep_data[0:(ni*nj)]


  # Create coordinates from the dx and dy values via a cumulative summation.
  # There may be a problem with this (feels too easy) but it is a rough first
  # cut.  Also, need to determine what the dx and dy values are relative to --
  # the CMS grids are cell centered and the resulting grid needs to reflect
  # this.
  grid = meshgrid(cumsum(dx_vals), cumsum(dy_vals))

  # Return list of lat, lon tuples.  Grid is flattend using 'F' for Fortran
  # ordering.
  return zip(grid[0].flatten('F'), grid[1].flatten('F'))


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
  wgs84 = Proj(init = 'epsg:4326')

  grid_origin = grid_info['grid_origin']
  lons, lats = transform(grid_proj, wgs84,
    grid_coords[0,:] + grid_origin[0],
    grid_coords[1,:] + grid_origin[1] )

  return zip(lons, lats)

