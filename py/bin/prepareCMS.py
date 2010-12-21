#!/usr/bin/env python

################################
# IMPORT MODULE FUNCTIONS
################################
import sys,os
libdir = os.path.abspath('.')+'/../lib/'
sys.path.insert( 0, libdir )
from wavecon import CMSman
from wavecon.config import CMSconfig

lon_ll = CMSconfig['lon_ll']
lat_ll = CMSconfig['lat_ll']
lon_ur = CMSconfig['lon_ur']
lat_ur = CMSconfig['lat_ur']
tmpdir = CMSconfig['tmpdir']

################################
# EXECUTABLE SECTION
################################
if __name__ == '__main__':
  
  #DEFINE SPATIAL DOMAIN
  box = CMSman.makebox()
  grid = CMSman.makegrid()

  #DEFINE TEMPORAL DOMAIN
  steeringtimes = CMSman.maketimes()  
  starttime = steeringtimes[0].strftime('%Y/%m/%d')
  stoptime = steeringtimes[len(steeringtimes)-1].strftime('%Y/%m/%d')

  #RETRIEVE WAVE DATA FROM DATABASE
  wavdata = CMSman.getwavedata(box,steeringtimes)
  if (wavdata==None):
    print '\n... downloading new data from WWIII ... \n'
    command = ' '.join(['./getWW3Spectra.py',lat_ur,lat_ll,
    lon_ur,lon_ll,starttime,stoptime,tmpdir])
    os.system(command)
    wavdata = CMSman.getwavedata(None,steeringtimes)

  #RETRIEVE WIND DATA FROM DATABASE
  windata = CMSman.getwinddata(None,steeringtimes)
  if (windata==None):
    print '\n... downloading new data from NAM12 ... \n'
    command = ' '.join(['./getNAM12Wind.py',lat_ur,lat_ll,
    lon_ur,lon_ll,starttime,stoptime,tmpdir])
    os.system(command)
    windata = CMSman.getwinddata(None,steeringtimes)
  
  #INTERPOLATE SPECTRA TO HALF_PLANE (NEW DIRECTIONAL BINS)
  wavdata = CMSman.interpolatespectra(wavdata)

  #FIND PEAK FREQUENCIES FOR EACH SPECTRA
  wavdata = CMSman.calculatepeakfreq(wavdata)

  #CREATE WAVE INPUT FILE AND MOVE TO CMS DIRECTORY
  if (wavdata==None):
    quit('\n WW3 ERROR: MISSING DATA \n')
  CMSman.gen_wavefiles(wavdata,steeringtimes)     
   
  #CREATE WIND INPUT FILE AND MOVE TO CMS DIRECTORY
  if (windata==None):
    quit('\n NAM12 ERROR: MISSING DATA \n')
  CMSman.gen_windfiles(windata,grid,steeringtimes)     
   
