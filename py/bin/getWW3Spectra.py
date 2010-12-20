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
from wavecon.config import DBconfig

################################
# CREATE DATABASE OBJECTS
################################
srctype = DBman.accessTable( DBconfig, 'tblsourcetype' )
src = DBman.accessTable( DBconfig, 'tblsource')
spec = DBman.accessTable( DBconfig, 'tblspectrabin' )
wave = DBman.accessTable( DBconfig, 'tblwave')

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
session = DBman.startSession( DBconfig )
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
    command = 'gunzip -f ' + tmpdir + '/' + filename  
    system(command)
    
    ################################
    # OPEN SESSION, ADD SOURCE TO tblSource
    ################################
    srcname = srctypename+'_'+date.strftime("%Y%m%d_%H")
    record = src(
        srcName=srcname,
        srcConfig='',
        srcBeginExecution=date.today(),
        srcEndExecution=date.today(),
        srcSourceTypeID=srctypeid)
    
    # add record to tblSource
    session = DBman.startSession( DBconfig )
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
        timestamps = timestamps[filter]
              
        # parse spectra, select only 24hrs of data
        spectra = num_match[(nfreqs+ndirs):]
        spectra = array(spectra)
        # convert from m^2/Hz/rad to m^2/Hz/degree         
        spectra = spectra * (pi/180)
        spectra = spectra.reshape(len(filter),nfreqs,ndirs)
        spectra = spectra[filter,:,:]
        spectra = spectra.tolist()
        
        ################################
        # ADD SPECTRAL BINS TO tblSpectra IF NECCESSARY
        ################################
        
        # determine whether bins exist in db 
        exists = False
        for rec in session.query(spec) :
            if (all((array(rec.spcdir) - array(dirs)) < .01) &
                all((array(rec.spcfreq) - array(freqs)) < .01)):
                exists = True
        
        # if bins don't exist in db, add them
        if (exists == False):
            record = spec(freqs,dirs)
            session.add(record)
            session.commit()
        
        # get spectra id for use in tblwave
        for rec in session.query(spec) :
            if (all((array(rec.spcdir) - array(dirs)) < .01) &
            all((array(rec.spcfreq) - array(freqs)) < .01)):         
                specid = rec.id
         
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
    print 'done with: '+str(date)+'\n'   

######TO DO###
####modulize
####add try/catch to system calls (skip date if wget failed)
