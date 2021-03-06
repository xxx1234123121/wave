"""
Overview
--------

This module provides a parser for CMS-Wave *.eng files.  These files contain
spectral input and output.

**Development Status:**
  **Last Modified:** December 29, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from numpy import array, linspace


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------
from wavecon.IO import FileScanner
from wavecon.util import maybe_float

from wavecon.config import CMSConfig
from wavecon import CMSman, GETman


#------------------------------------------------------------------------------
#  Spectral output parser
#------------------------------------------------------------------------------
def parse_eng_spectra(file_path):
  input = FileScanner(file_path)

  n_freq_bins, n_dir_bins = input.scan(2, int)

  freq_bins = input.scan(n_freq_bins, float)
  dir_bins = linspace(0, 180, n_dir_bins).tolist()


  # Instead of explicitly returning a list of spectra, we return a generator
  # here.  This is because CMS spectral output files can be quite large (one
  # day's worth of data from the Humboldt domain is ~7 GB!)
  def spectra():
    # Each spectral record is preceded by a 5-item header.  We assume that if
    # the header exists, an entire record will follow. When the FileScanner 
    # returns an empty list for the header, we have pulled all the spectra out
    # of the file.  Currently, the header is discarded.
    #
    # maybe_float is used to deal with the possibility of freak spectra numbers
    # that overflow the fortran output field producing '***' strings.  These
    # values get coded as NaN (and should probably be flagged with warnings).
    while input.scan(5):
      yield [ input.scan(n_dir_bins, maybe_float) for i in xrange(n_freq_bins) ]

  return {
    'freq_bins': freq_bins,
    'dir_bins': dir_bins,
    'spectra': spectra()
  }


#------------------------------------------------------------------------------
#  eng file generator
#------------------------------------------------------------------------------
def gen_eng_file(output_path, params):
  # This routine started out as makeWaveInput in prepareCMS.py

  model_config = CMSConfig(params['sim_name']).load_sim_config()

  #DEFINE SPATIAL/TEMPORAL DOMAIN
  box = CMSman.makebox(model_config)
  steeringtimes = CMSman.maketimes(params['sim_starttime'],
    params['sim_runtime'], params['sim_timestep'])

  #RETRIEVE WAVE DATA FROM DATABASE
  wavdata = CMSman.getwavedata(box, steeringtimes, model_config) #add wavtype
  if (wavdata==None):
    print '\n... downloading new wave data ... \n'
    GETman.getWAVE(model_config, params['sim_starttime'], params['sim_runtime'],
        params['sim_timestep'])
    wavdata = CMSman.getwavedata(box, steeringtimes, model_config) #add wavtype 

  # CONSTRUCT THE FILE
  CMSman.gen_wavefiles(wavdata, steeringtimes, model_config, output_path)

