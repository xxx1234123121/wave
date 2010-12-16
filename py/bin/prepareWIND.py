#!/usr/bin/env python

################################
# IMPORT MODULE FUNCTIONS
################################
import sys
from os import path,system
libdir = path.abspath('.')+'/../lib/'
sys.path.insert( 0, libdir )
from wavecon import prepareCMSinput
from wavecon.config import CMSconfig
from wavecon.config import DBconfig
from numpy import *
from math import sin,cos
from griddata import griddata

################################
# FOR EACH TIMESTEP, 
# INTERPOLATE TO GRID
# AND WRITE DATA TO WIND FILE
################################
def gen_windfiles(winfile,winspeed,windir,
wintime,winx,winy,steeringtimes,gridx,gridy):
  gridx=array(gridx)
  gridy=array(gridy)
  ugrid,vgrid=[[],[]]
  ny = len(gridx)
  nx = len(gridx[0])
  winfile = open(winfile,'w')
  line = str(nx)+' '+str(ny)+'\n'
  winfile.write(line)
  for mytime in steeringtimes:
    filter = (wintime==mytime)
    if (all(filter==False)): #CANT HANDLE MISSING DATA
      quit('\n\nno data exists for time: '+str(mytime)+
           '\n\nsuggested steering interval: '+str(wintime[1]-wintime[0]))
    else: #INTERPOLATE SINGLE TIMESTEP
      myx = winx[filter]
      myy = winy[filter]
      vel_x = winspeed[filter]*map(cos,windir[filter])
      vel_y = winspeed[filter]*map(sin,windir[filter])
      newvel_x = griddata(myx,myy,vel_x,gridx,gridy)    
      newvel_y = griddata(myx,myy,vel_y,gridx,gridy)
      #WRITE SINGLE TIMESTEP TO INPUT FILE
      winfile.write(mytime.strftime('%m%d%H')+'\n')
      lines = ['\n'.join([' '.join([str(newvel_x[i][j])+' '+
              str(newvel_y[i][j]) for j in range(nx)])]) 
              for i in range(ny)[::-1]]
      lines = '\n'.join(lines)
      winfile.write(lines+'\n')
  winfile.close()

if __name__ == '__main__':

  #define constants
  cmsdir   = CMSconfig['cmsdir']
  simfile  = CMSconfig['simfile']
  depfile  = CMSconfig['depfile']
  cardfile = CMSconfig['cardfile']
  nestfile   = CMSconfig['nestfile']
  metafile   = CMSconfig['metafile']
  windfile = CMSconfig['windfile']
  steeringinterval = CMSconfig['steeringinterval']

  #get spatial domain
  box,gridx,gridy = prepareCMSinput.spatialdomain(cmsdir,simfile,depfile)

  #get temporal domain
  starttime,stoptime,steeringtimes = \
      prepareCMSinput.temporaldomain(cmsdir,cardfile,steeringinterval)

  #retrieve records from database
  winspeed,windir,wintime,winx,winy = \
      prepareCMSinput.getwinddata(DBconfig,starttime,stoptime)

  #write data to cms input file
  gen_windfiles(windfile,winspeed,windir,wintime,winx,winy,steeringtimes,gridx,gridy)  
  system('mv '+windfile+' '+cmsdir) 
