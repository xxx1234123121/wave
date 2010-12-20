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
  grid = CMSman.makegrid()
  print '\nfound space\n'

  #DEFINE TEMPORAL DOMAIN
  steeringtimes = CMSman.maketimes()  
  print '\nfound time\n'

  #RETRIEVE DATA FROM DATABASE
  windata = CMSman.getwinddata(None,steeringtimes)
  print '\nfound data\n'
  
  #CREATE WIND INPUT FILE AND MOVE TO CMS DIRECTORY
  CMSman.gen_windfiles(windata,grid,steeringtimes)
  print '\ndone generating wind input file\n'
