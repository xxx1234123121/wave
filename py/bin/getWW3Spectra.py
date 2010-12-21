#!/usr/bin/env python
#SEE BELOW FOR COMMAND LINE ARGUMENTS
#EXAMPLE CALL: python getWW3Spectra.py 50 35 -120 -130 2010/12/10 2010/12/15 ~/Desktop/tmp

################################
# IMPORT MODULES
################################
import urllib #web support
import sys #argument parsing
import re #regex support
import glob #file wildcard support
import datetime #posix support
from numpy import * #math support
from geoalchemy import WKTSpatialElement
from os import path,system,remove
strptime = datetime.datetime.strptime

################################
# IMPORT DATABASE FUNCTIONS
################################
DBman_path = path.abspath('.')+'/../lib/'
sys.path.insert( 0, DBman_path )
from wavecon import DBman

################################
# CREATE DATABASE OBJECTS
################################
srctype = DBman.accessTable( None, 'tblsourcetype' )
src = DBman.accessTable( None, 'tblsource')
spec = DBman.accessTable( None, 'tblspectrabin' )
wave = DBman.accessTable( None, 'tblwave')

################################
# PARSE COMMAND LINE ARGUMENTS
################################
north =     sys.argv[1]       #50
south =     sys.argv[2]       #35
east =      sys.argv[3]       #-120
west =      sys.argv[4]       #-130
starttime = sys.argv[5]       #YYYY/MM/DD
stoptime =  sys.argv[6]       #YYYY/MM/DD
tmpdir =    sys.argv[7]       #/Users/naftali/Desktop/tmp
locale = 'EKA'

################################
# ADD WWIII TO tblSource
################################
session = DBman.startSession()
srctypename = 'WWIII'
existing = session.query(srctype)\
    .filter( srctype.sourcetypename == srctypename )

if (existing.first() == None):
    record = srctype(srctypename)
    session.add(record)
    session.commit()

# determine sourcetypeid to use in tblsource
srctypeid = session.query(srctype)\
    .filter( srctype.sourcetypename == srctypename )\
    .first().id

session.close()
session.bind.dispose()

################################
# PARSE DATE PARAMATERS
################################
starttime = strptime( starttime, '%Y/%m/%d' )
stoptime = strptime( stoptime, '%Y/%m/%d' )
delta = datetime.timedelta(1) # 24 hour increment
if (starttime==stoptime):
    stoptime = starttime + delta

################################
# COMPILE REGEX PATTERNS
################################
freqdir_pat = re.compile("III.*?(\d+).*?(\d+)")
num_pat = re.compile("-*\d+\.*\d+E.\d+")
timestamp_pat = re.compile("\d{8} \d{6}")
latlon_pat = re.compile("\d+.\d+-\d+.\d+")

################################
# GET DATA FOR EACH DAY, PARSE, THEN ADD TO DB 
################################
date = starttime
while date < stoptime :

    # build url string, download/gunzip files
    datestr = date.strftime("%Y%m%d") + '.t00z'
    url = 'ftp://polar.ncep.noaa.gov/pub/waves/latest_run/' 
    filename = 'enp.' + locale + '*'
    command = '{0} {1} {2}/{3}'.format('wget -A.gz -qP',tmpdir,url,filename)
    system(command)
    command = 'gunzip -qf ' + tmpdir + '/' + filename  
    system(command)
    
    ################################
    # OPEN SESSION, ADD SOURCE TO tblSource
    ################################
    
    # choose srcname
    for i in range(1000):
      srcname = srctypename+'_'+date.strftime("%Y%m%d_%H")+'_'+str(i)
      existing = session.query(src).filter( src.srcname == srcname )
      if (existing.first() == None):
          break
    
    #create record for tblsource
    record = src(
        srcName=srcname,
        srcConfig='',
        srcBeginExecution=date.today(),
        srcEndExecution=date.today(),
        srcSourceTypeID=srctypeid)
    
    # add record to tblSource
    session = DBman.startSession()
    session.add(record)
    session.commit()
    
    # get source id to use in tblwave
    srcid = session.query(src)\
        .filter( src.srcname == srcname )\
        .first().id

    ################################
    # LOOP THROUGH DOWNLOADED FILES
    ################################

    files = glob.glob(tmpdir + '/' + filename)
    for file in files:
        
        # store in long string, then delete file
        lines = open(file).read()

        # look for matches
        freqdir_match = freqdir_pat.search(lines)
        num_match = num_pat.findall(lines) 
        num_match = map(float,num_match)
        timestamp_match = timestamp_pat.findall(lines)
        latlon_match = latlon_pat.findall(lines)  
        
        # parse lat/lon
        lat = latlon_match[0][0:5]
        lon = latlon_match[0][5:]
        loc = WKTSpatialElement('POINT('+lon+' '+lat+')')
        
        # parse freq/dir bins
        # NOTE DIRS = DIRECTION OF TRAVEL
        nfreqs = int(freqdir_match.group(1))  
        ndirs = int(freqdir_match.group(2))
        freqs = num_match[0:nfreqs]
        dirs = num_match[nfreqs:(nfreqs+ndirs)]        
        dirs = map(degrees,dirs)
        
        # convert from numpy.float to float
        freqs = array(freqs).tolist()
        dirs = array(dirs).tolist()
                          
        # parse dates, select only 24hrs of data
        timestamps = [strptime( ts, '%Y%m%d %H0000' ) for ts in timestamp_match]
        timestamps = array(timestamps)
        filter = (timestamps >= date) & (timestamps < (date+delta))
        if (all(filter==False)):
          quit('error: cannot find valid timesteps in WW3 datafile: '+file)
        timestamps = timestamps[filter]
              
        # parse spectra, select only 24hrs of data
        spectra = num_match[(nfreqs+ndirs):]
        spectra = array(spectra)
        spectra = spectra * (pi/180) #m^2/Hz/rad to m^2/Hz/degree         
        spectra = spectra.reshape(len(filter),nfreqs,ndirs)
        spectra = spectra[filter,:,:]
        spectra = spectra.tolist()
        
        ################################
        # ADD SPECTRAL BINS TO tblSpectra IF NECCESSARY
        ################################
        
        # determine whether bins exist in db 
        exists = False
        for rec in session.query(spec):
            dirshape = array(rec.spcdir).size==array(dirs).size
            freqshape = array(rec.spcfreq).size==array(freqs).size
            dirval = all((array(rec.spcdir) - array(dirs)) < .01)
            freqval = all((array(rec.spcfreq) - array(freqs)) < .01)
            if (dirshape and freqshape and dirval and freqval):
                exists = True
                specid = rec.id  
                break         
 
        # if bins don't exist in db, add them
        if (exists == False):
            record = spec(freqs,dirs)
            session.add(record)
            session.commit()
            specid = record.id
         
        ################################
        # ADD DATA TO tblWave
        ################################
        for i in range(len(timestamps)):
            myspec = spectra[i]
            record = wave(
                wavSourceID=srcid, 
                wavSpectraBinID=specid, 
                wavLocation=loc, 
                wavDateTime=timestamps[i],  
                wavSpectra=myspec, 
                wavHeight=None, 
                wavPeakDir=None, 
                wavPeakPeriod=None)
            session.add(record)
        session.commit()
    
    ################################
    #CLOSE SESSION, REMOVE FILES, MOVE TO NEXT DAY    
    ################################
    session.close()
    session.bind.dispose()   
    command = 'rm -f '+' '.join(files)
    system(command)
    date = date+delta
    
######TO DO###
####modulize
####add try/catch to system calls (skip date if wget failed)
