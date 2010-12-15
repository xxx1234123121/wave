#!/usr/bin/env python

################################
# IMPORT MODULE FUNCTIONS
################################
import sys
from os import path
libdir = path.abspath('.')+'/../lib/'
sys.path.insert( 0, libdir )
from wavecon import prepareCMSinput
from numpy import *

################################
# INTERPOLATE SPECTRA TO NEW
# DIRECTION BINS, CMS EXPECTS 
# HALF PLANE DIVIDED INTO 'N' BINS,
# FIRST BIN = TRAVELING SOUTH,
# MIDDLE BIN = TRAVELING EAST, 
# LAST BIN = TRAVELING NORTH 
################################
def interpolatespectra(spec,dir):
  for k in range(len(spec)):
    filter = dir[k]>90
    dir[k][filter] = dir[k][filter]-360
    sortorder = argsort(dir[k])
    sorted_dirs = dir[k][sortorder]
    mydirs = linspace(-90,90,len(dir[k]))
    for f in range(len(spec[k])):
      sorted_spec = spec[k][f][sortorder]
      spec[k][f] = interp(mydirs,sorted_dirs,sorted_spec)
    return [spec,mydirs]

################################
# FOR EACH SPECTRA, FIND PEAK FREQUENCY
################################
def calculatepeakfreq(spec,freq):
  peakfreqindex = spec.max(1).argmax(1)
  peakfreq = []
  k=0
  for index in peakfreqindex:
    peakfreq.append(freq[k][index])
    k=k+1
  return [peakfreq[0]]


################################
# ARRANGE SPEC BY LOCATION, THEN TIME
################################
def gen_wavefiles(metafn,nestfn,wavtime,wavloc,wavx,wavy,freq,mydirs,steeringtimes,spec):
  locset = [x for x in set(wavloc)]
  sortorder = argsort(locset)
  locset = array(locset)[sortorder]                 
  #WRITE METAFILE HEADER
  metafile = open(metafn,'w')
  metafile.write(nestfn+'\n')
  metafile.write(str(len(locset))+'\n0\n')
  counter=0
  for myloc in locset:
    #CHECK THAT ALL FREQUENCY BINS MATCH
    filter = (wavloc==myloc)
    myfreq = freq[filter].tolist()
    nf = len(myfreq[0])
    nd = len(mydirs)
    myfreqstr = [' '.join([str(i) for i in f]) for f in myfreq]
    if (len(set(myfreqstr))>1):
      quit('error: frequency bin mismatch!')
    fn = 'WAVE.'+str(counter)+'.eng'
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
        quit('\n\nno data exists for time: '+str(mytime)+
            '\n\nsuggested steering interval: '+str(wavtime[1]-wavtime[0]))
      else:
        #WRITE SINGLE TIMESTEP DATA TO SPEC FILE
        filter = filter.tolist().index(True) 
        line = ' '.join([
          str(mytime.strftime('%m%d%H')),'0','0',
          str(peakfreq[filter]),'0'])
        file.write(line+'\n')
        for f in range(len(freq[filter])):
          line = ' '.join([str(d) for d in spec[filter][f]])
          file.write('\t'+line+'\n')
    file.close()
  metafile.close()
  # MERGE ENG FILES
  system('./mergeENG.exe < '+metafn)
  system('rm *.eng')
  system('mv '+nestfn+' '+cmsdir)

# EXECUTABLE SECTION
if __name__ == '__main__':
  
  #define constants
  cmsdir   = prepareCMSinput.cmsdir
  simfile  = prepareCMSinput.simfile
  depfile  = prepareCMSinput.depfile
  cardfile = prepareCMSinput.cardfile
  nestfn   = prepareCMSinput.nestfn
  metafn   = prepareCMSinput.metafn
  steeringinterval = prepareCMSinput.steeringinterval
  DBconfig = prepareCMSinput.DBconfig  

  #get spatial domain
  box,gridx,gridy = prepareCMSinput.spatialdomain(cmsdir,simfile,depfile)

  #get temporal domain
  starttime,stoptime,steeringtimes = \
      prepareCMSinput.temporaldomain(cmsdir,cardfile,steeringinterval)
  
  #retrieve records from database
  spec,specid,wavtime,wavloc,wavx,wavy,freq,dir = \
      prepareCMSinput.getwavedata(DBconfig,starttime,stoptime,box)
  
  #interpolate to new directional bins
  spec,mydirs = interpolatespectra(spec,dir)  
  
  #calculate peak frequencies
  peakfreq = calculatepeakfreq(spec,freq)
  
  #write data to cms input file
  gen_wavefiles(metafn,nestfn,wavtime,wavloc,wavx,wavy,freq,mydirs,steeringtimes,spec) 
