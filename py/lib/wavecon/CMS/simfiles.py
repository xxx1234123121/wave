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
from wavecon.config import CMS_TEMPLATES


#------------------------------------------------------------------------------
#  *.sim file generator
#------------------------------------------------------------------------------
SIM_DEFAULT_PARAMS = {

}


def gen_sim_file(output_path, params = SIM_DEFAULT_PARAMS):
  sim_template = CMS_TEMPLATES.get_template('WAVE.sim')

  with open(oputput_path, 'w') as sim_output:
    sim_output.writelines(sim_template.render(**params))

  return None

