#!/usr/bin/env python

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

################################
# IMPORT UBIQUITOUS FUNCTIONS
################################
from os import path,system
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
spec = DBman.accessTable( DBconfig, 'tblspectra' )
wave = DBman.accessTable( DBconfig, 'tblwave')

################################
# PARSE COMMAND LINE ARGUMENTS
################################
north =      50                                           # sys.argv[1]       #50
south =      35                                           # sys.argv[2]       #35
east =       -120                                         # sys.argv[3]       #-120
west =       -130                                         # sys.argv[4]       #-130
starttime =  '2010/07/29'                                   # sys.argv[5]       #YYYY/MM/DD
stoptime =   '2010/07/29'                                   # sys.argv[6]       #YYYY/MM/DD
tmpdir =     '/Users/naftali/Desktop/tmp'                   # sys.argv[7]       #/Users/naftali/Desktop/tmp
locale = 'EKA'

################################
# ADD WWIII TO tblSource
################################
session = DBman.startSession( DBconfig )
srcname = 'WWIII'
existing = session.query(srctype)\
    .filter( srctype.sourcetypename == srcname )

if (existing.first() == None):
    record = srctype(srcname)
    session.add(record)
    session.commit()

# determine sourcetypeid to use in tblsource
srctypeid = session.query(srctype)\
    .filter( srctype.sourcetypename == srcname )\
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
    url = 'ftp://polar.ncep.noaa.gov/pub/waves/' 
    filename = 'enp.' + locale + '*'
    command = '{0} {1} {2}/{3}/{4}'.format('wget -A.gz -qP',tmpdir,url,datestr,filename)
    system(command)
    command = 'gunzip ' + tmpdir + '/' + filename
    system(command)
    
    # loop through downloaded files
    files = glob.glob(tmpdir + '/' + filename)
    session = DBman.startSession( DBconfig )
    for file in files:
        # store file in long string
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
        loc = WKTSpatialElement('POINT('+lat+' '+lon+')')
        
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
        # convert spectra from numpy array to list
        spectra = spectra.tolist()
        
        
        ################################
        # ADD SPECTRAL BINS TO tblSpectra IF NECCESSARY
        ################################
        
        # determine whether bins exist in db 
        exists = False
        for rec in session.query(spec) :
            if (all((array(rec.spectradir) - array(dirs)) < .01) &
            all((array(rec.spectradir) - array(dirs)) < .01)):
                exists = True
        
        if (exists == False):
            record = spec(freqs,dirs)
            session.add(record)
            session.commit()
        
        for rec in session.query(spec) :
            if (all((array(rec.spectradir) - array(dirs)) < .01) &
            all((array(rec.spectradir) - array(dirs)) < .01)):         
                specid = rec.id
         
        ################################
        # ADD SOURCE TO tblSource
        ################################
        srcname = srcname+'_'+date.strftime("%Y%m%d_%H")
        record = src(
            srcName=srcname,
            srcConfig='',
            srcBeginExecution=date.today(),
            srcEndExecution=date.today(),
            srcSourceTypeID=srctypeid)
        
        # add record to tblSource
        session.add(record)
        session.commit()
        
        # get source id to use in tblwave
        srcid = session.query(src)\
            .filter( src.srcname == srcname )\
            .first().id
        
        ################################
        # ADD DATA TO tblWave
        ################################
        for i in range(len(timestamps)):
            myspec = spectra[i]
            record = wave(
                wavSourceID=srcid, 
                wavSpectraID=specid, 
                wavLocation=loc, 
                wavDateTime=timestamps[i],  
                wavSpectra=myspec, 
                wavHeight=None, 
                wavPeakDir=None, 
                wavPeakPeriod=None)
            session.add(record)
        
        session.commit()
    
    #DONE LOOPING THROUGH FILES, MOVE TO NEXT DAY    
    session.close()
    session.bind.dispose()   
    date = date+delta    
        
###TO DO###
#modulize
#add try/catch to system calls (skip date if wget failed)
