#!/usr/bin/env python

################################
# IMPORT MODULES AND CONFIG SETTINGS
################################
import os #run system commands
import datetime #sposix support
import glob #file wildcard support
import re #regex support
from numpy import * #math support
import DBman
from math import sin,cos,atan2,degrees
from griddata import griddata
strptime = datetime.datetime.strptime

import tempfile
import shutil

################################
# DEFINE POSTGIS BOX-OBJECT
################################
def makebox(model_config):

    west = model_config['west']
    south = model_config['south']
    east = model_config['east']
    north = model_config['north']
    projection = model_config['projection']
    
    #create box2d object (in projected coordinates)
    point_ll = 'ST_TRANSFORM(ST_SETSRID(ST_POINT('+west+','+south+'),4236),'+projection+')'
    point_ur = 'ST_TRANSFORM(ST_SETSRID(ST_POINT('+east+','+north+'),4326),'+projection+')'
    box = 'ST_SETSRID(ST_MAKEBOX2D('+point_ll+','+point_ur+'),'+projection+')'
    return box

################################
# DEFINE THE WAVE GRID FOR INTERPOLATION
################################
def makegrid(model_config):

    west = model_config['west']
    south = model_config['south']
    east = model_config['east']
    north = model_config['north']
    nx = int(model_config['nx'])
    ny = int(model_config['ny'])
    projection = model_config['projection']
    
    #build query
    point_ll = 'ST_TRANSFORM(ST_SETSRID(ST_POINT('+west+','+south+'),4236),'+projection+')'
    point_ur = 'ST_TRANSFORM(ST_SETSRID(ST_POINT('+east+','+north+'),4326),'+projection+')'  
    query = 'select ST_X('+point_ll+'),ST_Y('+point_ll+'),ST_X('+point_ur+'),ST_Y('+point_ur+')'
    
    #execute query
    session = DBman.startSession()
    result = session.execute(query).fetchall()
    west,south,east,north = result[0] 
    session.close()
    session.bind.dispose()  

    #create meshgrid object 
    gridx = linspace(float(west),float(east),nx)
    gridy = linspace(float(south),float(north),ny)
    grid = meshgrid(gridx,gridy)
    return grid

################################
# CALCULATE STEERING TIMES
################################
def maketimes(starttime,simduration,steeringinterval, return_timestamps = True):
      #create datetime objects  
      simduration = datetime.timedelta(float(simduration)/24.0)
      steeringinterval = datetime.timedelta(float(steeringinterval)/24.0)
      stoptime = starttime+simduration

      #determine steering times
      steeringtimes = []
      steeringsteps = []
      mytime = starttime
      while( mytime <= stoptime ):
          steeringtimes.append(mytime)
          steeringdiff = mytime - starttime
          steeringsteps.append(steeringdiff.days*24 +
                  steeringdiff.seconds/3600)
          mytime = mytime+steeringinterval

      if return_timestamps:
          return steeringtimes
      else:
          return steeringsteps

################################
# RETREIVE DATA FROM TBLWAVE
################################
def getwavedata(box, steeringtimes, model_config):
    #define constants
    projection = model_config['projection']
    starttime = steeringtimes[0]
    stoptime = steeringtimes[len(steeringtimes)-1]
    starttime = starttime.strftime('%Y%m%d %H:00' )
    stoptime = stoptime.strftime('%Y%m%d %H:00' )
    starttime = '(TIMESTAMP \''+starttime+'\')'
    stoptime = '(TIMESTAMP \''+stoptime+'\')'
  
    #construct query
    q1 = ' select wavid from tblwave '
    q2 = ' where ST_WITHIN(ST_TRANSFORM( '
    q3 = ' wavlocation,'+projection+'),'+box+')'
    q4 = ' and wavdatetime>='+starttime
    q5 = ' and wavdatetime<='+stoptime
    subquery = q1+q2+q3+q4+q5
    q1 = ' select wavspectra,wavspectrabinid,'
    q2 = ' wavdatetime,wavlocation,'
    q3 = ' ST_X(ST_TRANSFORM(wavlocation,'+projection+')),'
    q4 = ' ST_Y(ST_TRANSFORM(wavlocation,'+projection+')) '
    q5 = ' from tblwave where wavid in ('+subquery+')'
    query = q1+q2+q3+q4+q5
    
    #execute query
    session = DBman.startSession()
    result = session.execute(query).fetchall()
    if (len(result)==0): return None
      
    #parse result of query
    spec,specid,wavtime = [[],[],[]]
    wavloc,wavx,wavy = [[],[],[]]
    for k in range(len(result)):
        spec.append(result[k][0])
        specid.append(result[k][1])
        wavtime.append(result[k][2])
        wavloc.append(result[k][3])
        wavx.append(result[k][4])
        wavy.append(result[k][5])
    spec=array(spec)
    specid=array(specid)
    wavtime=array(wavtime)
    wavloc=array(wavloc)
    wavx=array(wavx)
    wavy=array(wavy)       
    
    #retreive freq/dir bins
    freq,dir = [[],[]]
    for myspectraid in specid:
        q1 = "select spcfreq,spcdir from "
        q2 = "tblspectrabin where spcid='"+myspectraid+"'"
        query = q1+q2
        result = session.execute(query).fetchall()
        freq.append(result[0][0])
        dir.append(result[0][1])            
    freq=array(freq)
    dir=array(dir)
    
    #close session and return
    session.close()
    session.bind.dispose()
    wavdata = {
      'spec':spec,'time':wavtime,'x':wavx,
      'y':wavy,'freq':freq,'dir':dir,'loc':wavloc}
    return wavdata

################################
# RETREIVE DATA FROM TBLWIND
################################
def getwinddata(box, steeringtimes, model_config):

    #define constants
    projection = model_config['projection']
    starttime = steeringtimes[0]
    stoptime = steeringtimes[len(steeringtimes)-1]
    starttime = starttime.strftime('%Y%m%d %H:00' )
    stoptime = stoptime.strftime('%Y%m%d %H:00' )
    starttime = '(TIMESTAMP \''+starttime+'\')'
    stoptime = '(TIMESTAMP \''+stoptime+'\')'

    #construct query
    q1 = ' select winid from tblwind where'
    q2 = ' windatetime>='+starttime
    q3 = ' and windatetime<='+stoptime
    subquery = q1+q2+q3
    if (box != None):
        q4 = ' and ST_WITHIN(ST_TRANSFORM( '
        q5 = ' winlocation,'+projection+'),'+box+')'
        subquery = subquery+q4+q5
    q1 = ' select winspeed,windirection,windatetime,'
    q2 = ' ST_X(ST_TRANSFORM(winlocation,'+projection+')),'
    q3 = ' ST_Y(ST_TRANSFORM(winlocation,'+projection+')) '
    q4 = ' from tblwind where winid in ('+subquery+')'
    query = q1+q2+q3+q4

    #execute query
    session = DBman.startSession()
    result = session.execute(query).fetchall()
    if (len(result)==0): return None

    #parse results
    wintime, winx, winy = [[],[],[]]
    winspeed, windir, winid = [[],[],[]] 
    for k in range(len(result)):
        winspeed.append(result[k][0])
        windir.append(result[k][1])
        wintime.append(result[k][2])
        winx.append(result[k][3])
        winy.append(result[k][4])
    winspeed=array(winspeed)
    windir=array(windir)
    wintime=array(wintime)
    winx=array(winx)
    winy=array(winy)

    #close session and return
    session.close()
    session.bind.dispose()
    windata = {
        'speed':winspeed,'dir':windir,
        'time':wintime,'x':winx,'y':winy }
    return windata

################################
# INTERPOLATE SPECTRA TO NEW
# DIRECTION BINS, CMS EXPECTS 
# HALF PLANE DIVIDED INTO 'N' BINS,
# FIRST BIN = TRAVELING SOUTH,
# MIDDLE BIN = TRAVELING EAST, 
# LAST BIN = TRAVELING NORTH 
################################
def interpolatespectra(wavdata):
  
    spec = wavdata['spec']
    dir = wavdata['dir']
    
    #cycle through each spectra
    for k in range(len(spec)):
        filter = dir[k]>90
        dir[k][filter] = dir[k][filter]-360
        sortorder = argsort(dir[k])
        sorted_dirs = dir[k][sortorder]
        mydirs = linspace(-90,90,len(dir[k]))
        #cycle through each frequency-row of spectra
        for f in range(len(spec[k])):
            sorted_spec = spec[k][f][sortorder]
            spec[k][f] = interp(mydirs,sorted_dirs,sorted_spec)
            dir[k] = array(mydirs)

    #push new values into wavdata and return
    wavdata['spec']=array(spec)
    wavdata['dir']=array(dir)
    return wavdata

################################
# FOR EACH SPECTRA, FIND PEAK FREQUENCY
################################
def calculatepeakfreq(wavdata):
  
    spec = wavdata['spec']
    freq = wavdata['freq']

    peakfreqindex = spec.max(1).argmax(1)
    peakfreq = []
    k=0
    for index in peakfreqindex:
        peakfreq.append(freq[k][index])
        k=k+1

    #push new values into wavdata
    wavdata['peakfreq'] = array(peakfreq)
    return wavdata

################################
# GENERATE A CMS SPECTRA FILE 
################################
def gen_wavefiles(wavdata, steeringtimes, model_config, output_path):
 
    if (wavdata==None):
      quit('\n CANNOT GENERATE INPUT FILE: MISSING WAVE DATA \n')
    
    wavdata = interpolatespectra(wavdata)
    wavdata = calculatepeakfreq(wavdata)  

    tmpdir = tempfile.gettempdir()
    nestfn = 'nest.dat'
    metafn = 'nest.meta'

    loc = wavdata['loc']
    freq = wavdata['freq']
    dir = wavdata['dir']
    wavx = wavdata['x']
    wavy = wavdata['y']
    wavloc = wavdata['loc']
    wavtime = wavdata['time']
    peakfreq = wavdata['peakfreq']
    spec = wavdata['spec']

    # GAAAAAAAAAAAAAAAAAAAAAAAAAAAH.  Ugly Ugly hack. It hurts me to do this.
    windat = os.path.dirname(output_path)
    winfile = glob.glob(windat + '/*.ave')[0]
    winfile = open(winfile, 'r')
    windat = winfile.read().splitlines()
    winfile.close()
    win_dat = [(speed, direc) for speed, direc in (line.split() for
        line in windat)]
    
    #FIND DISTINCT LOCATIONS
    locset = [x for x in set(loc)]
    sortorder = argsort(locset)
    locset = array(locset)[sortorder]
    
    #WRITE METAFILE HEADER
    nestfn = '/'.join([tmpdir,nestfn])
    metafn = '/'.join([tmpdir,metafn])
    metafile = open(metafn,'w')
    metafile.write(nestfn+'\n')
    metafile.write(str(len(locset))+'\n0\n')
    counter=0
    for myloc in locset:
      wind = iter(win_dat)
      #CHECK THAT ALL FREQUENCY BINS MATCH
      filter = (loc==myloc)
      myfreq = freq[filter].tolist()
      nf = len(myfreq[0])
      nd = len(dir[0])
      myfreqstr = [' '.join([str(i) for i in f]) for f in myfreq]
      if (len(set(myfreqstr))>1):
        quit('error: frequency bin mismatch!')
      fn = 'WAVE.'+str(counter)+'.eng'
      fn = '/'.join([tmpdir,fn])
      counter=counter+1
      #ADD META DATA TO METAFILE
      myx = set(wavx[filter])
      myy = set(wavy[filter])
      if (len(myx)>1 or len(myy)>1):
        quit('error: coordinate mismatch!')
      myx = wavx[filter][0]
      myy = wavy[filter][0]
      metafile.write(fn+'\n')
      metafile.write(str(myx)+' '+str(myy)+'\n')
      #WRITE SPEC FILE HEADER
      file=open(fn,'w')
      file.write( str(nf) + ' ' + str(nd) + '\n' )
      file.write( myfreqstr[0] + '\n')
      #WRITE CONSECUTIVE TIMESTEPS TO FILE 
      for mytime in steeringtimes:
        filter = logical_and( wavloc==myloc, wavtime==mytime)
        if (all(filter==False)):
          #CANT HANDLE MISSING DATA
          quit('\n\nno data exists for time: '+str(mytime)+'\n\n')
        else:
          #WRITE SINGLE TIMESTEP DATA TO SPEC FILE
          filter = filter.tolist().index(True)
          win_speed, win_dir = wind.next()
          line = ' '.join([
            str(mytime.strftime('%m%d%H')),win_speed,win_dir,
            str(peakfreq[filter]),'0'])
          file.write(line+'\n')
          for f in range(len(freq[filter])):
            line = ' '.join([str(d) for d in spec[filter][f]])
            file.write('\t'+line+'\n')
      file.close()
    metafile.close()
    winfile.close()
    os.system('mergeENG < '+metafn)
    os.system('rm /'+tmpdir+'/*.eng '+metafn)
    shutil.copy(nestfn, output_path)
    return 

################################
# GENERATE A CMS WIND FILE 
################################
def gen_windfiles(windata,grid,steeringtimes,model_config,output_path):

  if (windata==None):
    quit('\n CANNOT GENERATE INPUT FILE: MISSING WIND DATA \n')

  #import constants
  tmpdir = tempfile.gettempdir()
  nx = int(model_config['nx'])
  ny = int(model_config['ny'])
  winspeed = windata['speed']
  windir = windata['dir']
  wintime = windata['time']
  winx = windata['x']
  winy = windata['y']
  gridx=array(grid[0])
  gridy=array(grid[1])

  ugrid,vgrid=[[],[]]
  windfn = '/'.join([tmpdir,'wind.dat']) 
  avewindfn = '/'.join([tmpdir,'avewind.dat'])
  winfile = open(windfn,'w')
  avewinfile = open(avewindfn, 'w')
  line = str(nx)+' '+str(ny)+'\n'
  winfile.write(line)
  for mytime in steeringtimes:
    filter = (wintime==mytime)
    if (all(filter==False)): #CANT HANDLE MISSING DATA
      quit('\n\nno data exists for time: '+str(mytime)+'\n\n')
    else: #INTERPOLATE SINGLE TIMESTEP
      myx = winx[filter]
      myy = winy[filter]
      vel_x = winspeed[filter]*map(cos,windir[filter])
      vel_y = winspeed[filter]*map(sin,windir[filter])
      newvel_x = griddata(myx,myy,vel_x,gridx,gridy)
      newvel_y = griddata(myx,myy,vel_y,gridx,gridy)
      avevel_x = mean(newvel_x)
      avevel_y = mean(newvel_y)
      win_speed = sqrt(avevel_x**2 + avevel_y**2)
      win_dir = degrees(atan2(avevel_y, avevel_x))
      #WRITE SINGLE TIMESTEP TO INPUT FILE
      winfile.write(mytime.strftime('%m%d%H')+'\n')
      lines = ['\n'.join([' '.join([str(newvel_x[i][j])+' '+
              str(newvel_y[i][j]) for j in range(nx)])])
              for i in range(ny)[::-1]]
      lines = '\n'.join(lines)
      winfile.write(lines+'\n')
      avewinfile.write('{0} {1}\n'.format(win_speed, win_dir))
  winfile.close()
  avewinfile.close()
  os.system('mv ' + windfn + ' ' + output_path)
  os.system('mv ' + avewindfn + ' ' + output_path + '.ave')
  return
