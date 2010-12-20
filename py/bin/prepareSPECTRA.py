#!/usr/bin/env python

################################
# IMPORT MODULE FUNCTIONS
################################
import sys,os
libdir = os.path.abspath('.')+'/../lib/'
sys.path.insert( 0, libdir )
from wavecon import CMSman

################################
# EXECUTABLE SECTION
################################
if __name__ == '__main__':
  
  #DEFINE SPATIAL DOMAIN
  box = CMSman.makebox()
  print '\nfound space\n'

  #DEFINE TEMPORAL DOMAIN
  steeringtimes = CMSman.maketimes()  
  print '\nfound time\n'

  #RETRIEVE DATA FROM DATABASE
  wavdata = CMSman.getwavedata(box,steeringtimes)
  print '\nfound spectra\n'
  
  #INTERPOLATE TO HALF_PLANE (NEW DIRECTIONAL BINS)
  wavdata = CMSman.interpolatespectra(wavdata)
  print '\ninterpolated\n'

  #FIND PEAK FREQUENCIES FOR EACH SPECTRA
  wavdata = CMSman.calculatepeakfreq(wavdata)
  print '\nfound peak freqs\n'

  #CREATE SPECTRAL INPUT FILE AND MOVE TO CMS DIRECTORY
  CMSman.gen_wavefiles(wavdata,steeringtimes)
  print '\ndone generating spectral input\n'
