"""
Overview
--------

This module provides an interface to data stored in the XMDF output files
generated by CMS-Wave and CMS-Flow.  The XMDF data format is built upon HDF5 and
is readable using HDF tools.

**Development Status:**
  **Last Modified:** December 16, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from datetime import datetime, timedelta
from os import path
from glob import glob
from itertools import chain

from math import sqrt, atan2, degrees


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from numpy import array
import h5py


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------
from .cmcards import cmcards_parser
from .gridfiles import telfile_parser, georeference_grid


#------------------------------------------------------------------------------
#  Data Retrieval
#------------------------------------------------------------------------------
def postprocess_CMS_run(cmcardsPath):
  run_meta = load_run_metadata(cmcardsPath)

  grid = georeference_grid(
    telfile_parser(run_meta['grid_info']['telgrid_file']),
    run_meta['grid_info']
  )

  return {
    'run_info': run_meta['run_info'],
    'current_records': load_current_data(grid, run_meta['current_data'])
  }


def load_run_metadata(cmcardsPath):
  cmcards = cmcards_parser.parseFile(cmcardsPath)

  sim_dir = path.dirname(cmcardsPath)
  cmcards_file = path.splitext(path.basename(cmcardsPath))[0]
  # Brute force search for the wave sim file---probably a more elegant way to do
  # this.
  sim_file = glob(path.join(sim_dir,'*.sim'))
  if len(sim_file) != 0:
    sim_file = sim_file[0]
  else:
    raise IOError('''Could not find a CMS-wave *.sim file.  The directory:
        {0}
    Was searched for files ending in .sim'''.format(sim_dir))

  start_time = datetime.strptime(
    '{0} {1}'.format(
      cmcards.STARTING_JDATE[0],
      cmcards.STARTING_JDATE_HOUR[0]
    ), '%y%j %H' )

  stop_time = start_time + timedelta(hours = cmcards.DURATION_RUN[0])

  sim_label = cmcards.SIMULATION_LABEL[0]

  run_info = {
    'run_name':  '{0}-{1}'.format(cmcards_file, sim_label),
    'start_time': start_time,
    'stop_time': stop_time,
  }

  grid_info = {
    'grid_origin': (cmcards.GRID_ORIGIN_X[0], cmcards.GRID_ORIGIN_Y[0]),
    'grid_angle': cmcards.GRID_ANGLE[0],
    'telgrid_file': path.join(sim_dir, cmcards_file) + '.tel' 
  }

  if cmcards.GRID_EPSG_CODE:
    grid_info['grid_epsg_code'] = 'EPSG:{0}'.format(cmcards.GRID_EPSG_CODE[0])
  else:
    raise LookupError('''
    In order to properly georeference CMS output, this program needs to know the
    spatial reference system (SRS) in which the following grid origin is
    expressed:

        {0}

    This is done by adding a non-standard card, GRID_EPSG_CODE, to:

        {1}

    This card contains an integer specifying the EPSG code of the SRS.  EPSG
    codes can be looked up at:

        www.spatialreference.org
    '''.format(
      grid_info['grid_origin'], cmcardsPath)
    )

  current_data = {
    'data_file': path.join(sim_dir, cmcards.GLOBAL_VELOCITY_OUTPUT[0]),
    'current_vector': '/' + sim_label + '/Current_Velocity/Values',
    'output_timesteps': getDataOutputTimes('current', start_time, stop_time,
      cmcards)
  }

  wave_data = {
    'data_file': path.splitext(sim_file)[0] + '_out.h5',
    'output_timesteps': getDataOutputTimes('wave', start_time, stop_time,
      cmcards)
  }

  return {
    'run_info': run_info,
    'grid_info': grid_info,
    'current_data': current_data,
    'wave_data': wave_data
  }


def load_current_data(grid, current_info):
  data_file = h5py.File(current_info['data_file'], 'r')
  data_set = data_file[current_info['current_vector']]

  current_records = list(chain.from_iterable([
    [create_current_record(vector, location, timestep)
      for (vector, location) in zip(row,grid) ]
      for (row, timestep) in zip(data_set, current_info['output_timesteps'])
  ]))

  return current_records


#---------------------------------------------------------------------
#  Utility Functions
#---------------------------------------------------------------------
def compass_degrees(angle):
  '''Angle is assumed to be in radians!'''
  angle = 90 - degrees(angle)
  if angle < 0:
    return 360 + angle
  else:
    return angle


def create_current_record(vector, location, time):
  speed = sqrt(vector[0]**2 + vector[1]**2)
  direction = compass_degrees(atan2(vector[0], vector[1]))

  return {
    'speed': speed,
    'direction': direction,
    'location': location,
    'timestamp': time
  }


def getDataOutputTimes(data_type, start_time, stop_time, cmcards):
  if data_type == 'current':
    timestep_list = 'TIME_LIST_{0}'.format(cmcards.VEL_OUT_TIMES_LIST[0])
  elif data_type == 'wave':
    timestep_list = 'TIME_LIST_{0}'.format(cmcards.WAVES_OUT_TIMES_LIST[0])
  else:
    raise NotImplementedError('''Support for CMS output of type {0} has not been
    implemented yet.'''.format(data_type))

  output_timesteps = cmcards[timestep_list].asList()
  num_timesteps = output_timesteps.pop(0)

  # CMS accepts output timesteps as a list of three-tuples of the form:
  #
  # - Beginning time of new interval
  # - Length of interval
  # - Ending time of new interval
  #
  # For now we are going to assume that the important number is the beginning
  # time.  ***THIS IS A BIG ASSUMPTION***
  output_timesteps = [
    start_time + timedelta(hours = x)
    for x in array(output_timesteps)[range(0, num_timesteps, 3)]
    if timedelta(hours = x) <= (stop_time - start_time)
  ]

  return output_timesteps

