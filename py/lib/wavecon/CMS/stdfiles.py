"""
Overview
--------

This module provides functions for creating *.std files--one of the inputs for
CMS-Flow.

**Development Status:**
  **Last Modified:** December 22, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from numpy import meshgrid


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------
from wavecon.config import CMS_TEMPLATES, CMSConfig


#------------------------------------------------------------------------------
#  .std file generator
#------------------------------------------------------------------------------
# Defaults taken from the Humbold bay simulation.
STD_DEFAULT_PARAMS = {
  'iprp':  0,
  'icur':  0,
  'ibrk':  0,
  'irs':   0,
  'ibnd':  0,
  'iwet':  0,
  'ibf':   0,
  'iark':  0,
  'iarkr': 0,
  'akap':  4.0,
  'bf':    0.005,
  'ark':   0.5,
  'arkr':  0.3,
  'iwvbk': 0
}

def gen_std_file(output_path, sim_name, params = STD_DEFAULT_PARAMS):
  std_template = CMS_TEMPLATES.get_template('WAVE.std')

  model_config = CMSConfig(sim_name).load_sim_config()

  # Set up a grid for observation cells.  This could probably live in the
  # gridfiles module.
  nx = int(model_config['nx']); ny = int(model_config['ny'])
  grid = meshgrid(xrange(1, nx + 1), xrange(1, ny + 1))

  params['kout'] = nx * ny
  params['observation_cells'] = zip(grid[0].flatten('F'), grid[1].flatten('F'))

  with open(output_path, 'w') as std_output:
    std_output.writelines(std_template.render(**params))

  return None

