"""
Overview
--------

This module facilitates the setup of a CMS model run by copying static files and
rendering templates into a simulation directory.

**Development Status:**
  **Last Modified:** December 29, 2010 by Charlie Sharpsteen

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

  return None


#------------------------------------------------------------------------------
#  Utility Functions
#------------------------------------------------------------------------------


