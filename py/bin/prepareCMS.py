#!/usr/bin/env python

################################
# IMPORT MODULE FUNCTIONS
################################
import sys,os
libdir = os.path.abspath('.')+'/../lib/'
sys.path.insert( 0, libdir )
from wavecon import CMSman,GETman
from wavecon.config import CMSconfig
from datetime import timedelta

################################
# CREATE WIND INPUT
################################
def makeWindInput():
  
  #DEFINE SPATIAL/TEMPORAL DOMAIN
  grid = CMSman.makegrid()
  steeringtimes = CMSman.maketimes(None,None,None)  
  
  #RETRIEVE WIND DATA FROM DATABASE
  windata = CMSman.getwinddata(None,steeringtimes) #add wintype
  if (windata==None):
    print '\n... downloading new wind data ... \n'
    GETman.getWIND(CMSconfig)
    windata = CMSman.getwinddata(None,steeringtimes) #add wintype
  
  # CONSTRUCT THE FILE
  CMSman.gen_windfiles(windata,grid,steeringtimes)


################################
# CREATE WAVE INPUT
################################
def makeWaveInput():
    
    #DEFINE SPATIAL/TEMPORAL DOMAIN
    box = CMSman.makebox()
    steeringtimes = CMSman.maketimes(None,None,None)

    #RETRIEVE WAVE DATA FROM DATABASE
    wavdata = CMSman.getwavedata(box,steeringtimes) #add wavtype
    if (wavdata==None):
      print '\n... downloading new wave data ... \n'
      GETman.getWAVE(CMSconfig)
      wavdata = CMSman.getwavedata(box,steeringtimes) #add wavtype 
    
    # CONSTRUCT THE FILE
    CMSman.gen_wavefiles(wavdata,steeringtimes)

if __name__ == '__main__':
  
    makeWaveInput()
    makeWindInput()
