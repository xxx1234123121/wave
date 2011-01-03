"""
Overview
--------

This module facilitates the setup of a CMS model run by copying static files and
rendering templates into a simulation directory.

**Development Status:**
  **Last Modified:** January 1, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from os import getcwd, path, mkdir
from shutil import copy
import re


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------
from wavecon.config import CMSConfig
from .simfiles import gen_sim_file
from .cmcards import gen_cmcards_file
from .stdfiles import gen_std_file
from .engfiles import gen_eng_file


#------------------------------------------------------------------------------
#  Model Setup
#------------------------------------------------------------------------------
def setup_model_run(**kwargs):

  sim_dir = path.join(getcwd(), kwargs['sim_label'])

  if not path.isdir(sim_dir):
    mkdir(sim_dir)

  sim_info = CMSConfig(kwargs['sim_name'])

  # Copy static files containing bathymetry info into the simulation directory.
  for static_file in sim_info.static_files:
    file_ext = path.splitext(static_file)[1]
    if file_ext == '.h5':
      file_ext = '_' + re.split('_', path.basename(static_file)).pop()
    sim_file = path.join(sim_dir, kwargs['sim_name'] + file_ext)
    copy(static_file, sim_file)

  gen_sim_file(path.join(sim_dir, kwargs['sim_name'] + '.sim'), kwargs)
  gen_cmcards_file(path.join(sim_dir, kwargs['sim_name'] + '.cmcards'), kwargs)
  gen_std_file(path.join(sim_dir, kwargs['sim_name'] + '.std'), kwargs['sim_name'])

  gen_wind_file(path.join(sim_dir, kwargs['sim_name'] + '.wind'), kwargs)
  gen_eng_file(path.join(sim_dir, 'nest.dat'), kwargs)

  return None


#------------------------------------------------------------------------------
#  Utility Functions
#------------------------------------------------------------------------------

# This is living here for now because there is no other good place for it at the
# moment.

################################
# CREATE WIND INPUT
################################
def gen_wind_file(output_path, params):
  from wavecon import CMSman, GETman
  model_config = CMSConfig(params['sim_name']).load_sim_config()
  
  #DEFINE SPATIAL/TEMPORAL DOMAIN
  grid = CMSman.makegrid(model_config)
  steeringtimes = CMSman.maketimes(params['sim_starttime'],
    params['sim_runtime'], params['sim_timestep'])
  
  #RETRIEVE WIND DATA FROM DATABASE
  windata = CMSman.getwinddata(None,steeringtimes, model_config) #add wintype
  if (windata==None):
    print '\n... downloading new wind data ... \n'
    GETman.getWIND(model_config, params['sim_starttime'], params['sim_runtime'],
      params['sim_timestep'])
    windata = CMSman.getwinddata(None,steeringtimes, model_config) #add wintype
  
  # CONSTRUCT THE FILE
  CMSman.gen_windfiles(windata,grid,steeringtimes,model_config, output_path)


