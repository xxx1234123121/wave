"""
Overview
--------

This module contains routines for generating CMS-Wave *.sim files.


**Development Status:**
  **Last Modified:** December 29, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------
from wavecon.config import CMS_TEMPLATES, CMSConfig


#------------------------------------------------------------------------------
#  *.sim file generator
#------------------------------------------------------------------------------
DEFAULT_SIM_PARAMS = {'sim_name': 'humboldt-example'}

def gen_sim_file(output_path, params = DEFAULT_SIM_PARAMS):
  sim_template = CMS_TEMPLATES.get_template('WAVE.sim')
  sim_config = CMSConfig(params['sim_name']).load_sim_config()

  sim_config.update(params)

  with open(output_path, 'w') as sim_output:
    sim_output.writelines(sim_template.render(**sim_config))

  return None

