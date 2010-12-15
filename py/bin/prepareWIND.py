#!/usr/bin/env python

################################
# IMPORT MODULE FUNCTIONS
################################
import sys
from os import path
libdir = path.abspath('.')+'/../lib/'
sys.path.insert( 0, libdir )
from wavecon import prepareCMSinput

################################
# FOR EACH TIMESTEP, 
# INTERPOLATE TO GRID
# AND WRITE DATA TO WIND FILE
################################
def gen_windfiles(winfile,winspeed,windir,wintime,winx,winy,steeringtimes,gridx,gridy)
ugrid,vgrid=[[],[]]
nx = gridx.shape[0]
ny = gridx.shape[1]
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
    vel_x = winspeed[filter]*cos(windir[filter])
    vel_y = winspeed[filter]*sin(windir[filter])
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
  cmsdir   = prepareCMSinput.cmsdir
  simfile  = prepareCMSinput.simfile
  depfile  = prepareCMSinput.depfile
  cardfile = prepareCMSinput.cardfile
  windfile = prepareCMSinput.windfile 
  steeringinterval = prepareCMSinput.steeringinterval
  DBconfig = prepareCMSinput.DBconfig  
   
  #get spatial domain
  box,gridx,gridy = prepareCMSinput.spatialdomain(cmsdir,simfile,depfile)
  box = box[0]

  #get temporal domain
  starttime,stoptime,steeringtimes = \
      prepareCMSinput.temporaldomain(cmsdir,cardfile,steeringinterval)

  #retrieve records from database
  winspeed,windir,wintime,winx,winy = \
      prepareCMSinput.getwinddata(DBconfig,starttime,stoptime)
  
  #write data to cms input file
  gen_windfiles(winfile,winspeed,windir,wintime,winx,winy,steeringtimes,gridx,gridy)  
   
