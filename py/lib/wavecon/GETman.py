#!/usr/bin/env python
#SEE 'NAME==MAIN' SECTION FOR COMMAND LINE ARGUMENTS
#python -i GETman.py 50 35 -120 -130 2010122200 6 6 ~/Desktop/tmp NAM12 WW3 EKA

################################
# IMPORT MODULES 
################################
import urllib #web support
import datetime #posix support
import os,sys,re #argument parsing
import glob #file wildcards
from numpy import * #math support
from math import * #pi constant
from netCDF4 import * #netcdf support
from geoalchemy import WKTSpatialElement
from config import CMSconfig
import DBman,CMSman
strptime = datetime.datetime.strptime

################################
# CREATE DATABASE OBJECTS
################################
srctype = DBman.accessTable( None, 'tblsourcetype' )
src = DBman.accessTable( None, 'tblsource')
wind = DBman.accessTable( None, 'tblwind' ) 
wave = DBman.accessTable( None, 'tblwave' ) 
specbin = DBman.accessTable( None, 'tblspectrabin' )

################################
# ADD RECORD TO TBLSOURCETYPE IF NECESSARY
################################
def add_sourcetype(srctypename):
    
    print '\nadd_sourcetype slated for removal...use DB.py instead\n'

    #check if sourcetype exists
    session = DBman.startSession()     
    existing = session.query(srctype)\
        .filter( srctype.sourcetypename == srctypename )
    if ( existing.first() == None ):
        #if doesn't exist,  add new sourcetype to db
        record = srctype(srctypename)                              
        session.add(record)
        session.commit()
        srctypeid = record.id
    else:
        #if exists, get id for existing sourcetype
        srctypeid = session.query(srctype)\
        .filter( srctype.sourcetypename == srctypename )\
        .first().id
    session.close()
    session.bind.dispose()
    return srctypeid

################################
# ADD RECORD TO TBLSOURCE IF NECESSARY
################################
def add_source(srctypeid,date):
    
    print '\nadd_source slated for removal...use DB.py instead\n'
    
    # get the source type given an id
    session = DBman.startSession()
    srctypename = session.query(srctype)\
    .filter( srctype.sourcetypeid == srctypeid )\
    .first().sourcetypename
    
    # choose srcname
    for i in range(1000):
      srcname = srctypename+'_'+date.strftime("%Y%m%d_%H")+'_'+str(i)
      existing = session.query(src).filter( src.srcname == srcname )
      if (existing.first() == None):
          break

    # prepare record for tblSource
    record = src(
    srcName=srcname, 
    srcConfig='', 
    srcBeginExecution=date.today(), 
    srcEndExecution=date.today(), 
    srcSourceTypeID=srctypeid)
    
    # add record to tblSource
    session.add(record)    
    session.commit()
    srcid = record.id
    session.close()
    session.bind.dispose()
    return srcid

################################
# ADD RECORD TO TBLSPECTRABIN IF NECESSARY
################################
def add_spectrabin(freqs,dirs):

    # determine whether bins exist in db 
    exists = False
    session = DBman.startSession()
    for rec in session.query(specbin):
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
        record = specbin(freqs,dirs)
        session.add(record)
        session.commit()
        specid = record.id

    session.close()
    session.bind.dispose()
    return specid

##########################################
# DOWNLOAD LATEST WW3 DATA
##########################################
def ww3_download(wavregion,tmpdir):
    
    url = 'ftp://polar.ncep.noaa.gov/pub/waves/latest_run/'
    filename = 'enp.' + wavregion + '*'
    print '\ndownloading WW3 latest run...'       
    command1 = 'rm -f ' + tmpdir + '/' + filename
    command2 = '{0} {1} {2}/{3}'.format('wget -A.gz -qP',tmpdir,url,filename)
    command3 = 'gunzip -q ' + tmpdir + '/' + filename  
    flag = os.system(command1)                              
    if (flag!=0): quit('\nERROR: COULD NOT REMOVE EXISTING WW3 FILES')
    flag = os.system(command2)
    if (flag!=0): quit('\nERROR: COULD NOT DOWNLOAD WW3 DATA')
    flag = os.system(command3)
    if (flag!=0): quit('\nERROR: COULD NOT GUNZIP WW3 DATA')
    print 'done'
    files = glob(tmpdir + '/' + filename)
    return files

##########################################
# PARSE SINGLE WW3 DATAFILE
##########################################
def ww3_parsefile(file):

    #read file contents
    lines = open(file).read()
    
    # compile regex patterns
    freqdir_pat = re.compile("III.*?(\d+).*?(\d+)")
    num_pat = re.compile("-*\d+\.*\d+E.\d+")
    timestamp_pat = re.compile("\d{8} \d{6}")
    latlon_pat = re.compile("\d+.\d+-\d+.\d+")
    
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
    lat = float(lat)
    lon = float(lon)
    
    # parse freq/dir bins
    # NOTE DIRS = DIRECTION OF TRAVEL
    nfreqs = int(freqdir_match.group(1))
    ndirs = int(freqdir_match.group(2))
    freqs = num_match[0:nfreqs]
    dirs = num_match[nfreqs:(nfreqs+ndirs)]
    dirs = map(degrees,dirs)
    
    # parse dates 
    timestamps = [strptime( ts, '%Y%m%d %H0000' ) for ts in timestamp_match]
    
    # parse spectra
    spectra = num_match[(nfreqs+ndirs):]
    spectra = array(spectra)
    spectra = spectra * (pi/180) #m^2/Hz/rad to m^2/Hz/degree         
    spectra = spectra.reshape(len(timestamps),nfreqs,ndirs)
    spectra = spectra.tolist()  
  
    #reorganize into dictionary
    wavdata={}
    for i in range(len(timestamps)):
        wavdata[timestamps[i]] = {
        'loc':loc,'lat':lat,'lon':lon,
        'freqs':freqs,'dirs':dirs,
        'spectra':spectra[i] }
    return wavdata

##########################################
# ADD RECORDS TO TBLWAVE
##########################################
def push_wavdata(wavdata,srcid,specbinid):

    session = DBman.startSession()
    for loc in sort(wavdata.keys()):           
        
        for date in sort(wavdata[loc].keys()):
            
            # parse dictionary
            spectra = wavdata[loc][date]['spectra']  
            # add record to tblwave
            record = wave(
            wavSourceID=srcid,
            wavSpectraBinID=specbinid,
            wavLocation=loc,
            wavDateTime=date,
            wavSpectra=spectra,
            wavHeight=None,
            wavPeakDir=None,
            wavPeakPeriod=None)
            session.add(record)

    # close session
    session.commit()
    session.close()
    session.bind.dispose()
    return


##########################################
# RUN DOWNLOADER AND PARSER FOR WW3 DATA
##########################################
def getWW3(wavregion,tmpdir):
    wavdata = {}
    files = ww3_download(wavregion,tmpdir)
    for file in files:
        mywavdata = ww3_parsefile(file)
        date = mywavdata.keys()[0]
        wavdata[mywavdata[date]['loc']] = mywavdata
    return wavdata
    
################################
# DOWNLOAD NAM12 FILE 
################################
def nam12_download(date,north,south,east,west,tmpdir):
    print '\ndownloading NAM12 date: '+str(date)+'...'
    myurl = nam12_url(date,north,south,east,west)
    tmpfile = tmpdir + '/tmp.nc'
    command1 = 'rm -f ' + tmpfile
    command2 = '{0} {1} \'{2}\''.format('wget -qO',tmpfile,myurl)
    flag = os.system(command1)
    if (flag!=0): quit('\nERROR: COULD NOT REMOVE EXISTING NAM12 FILE')
    flag = os.system(command2)
    if (flag!=0): quit('\nERROR: COULD NOT DOWNLOAD NAM12 FILE')
    print 'done'
    return tmpfile

################################
# RUN DOWNLOADER AND PARSE NAM12 FILES
################################
def getNAM12(dates,north,south,east,west,tmpdir):
    
    windata={}
    for date in dates:
        # download datafile
        tmpfile = nam12_download(date,north,south,east,west,tmpdir)    
        
        # parse data
        ncdf = Dataset(tmpfile,'r',format='NETCDF4')
        ugrid = ncdf.variables['u_wind_height_above_ground'][:][0][0]
        vgrid = ncdf.variables['v_wind_height_above_ground'][:][0][0]
        lats = ncdf.variables['lat'][:]
        lons = ncdf.variables['lon'][:]
        os.unlink(tmpfile) 
        
        # convert from u/v to speed/direction, 
        # dir = cartesian coordinates 
        # (0 = traveling east, 90 = traveling north)     
        spd = (ugrid**2.0 + vgrid**2.0)**(1.0/2.0)
        dir = arctan2(vgrid,ugrid)   
        dir = dir*180./pi 
        
        # add date to dictionary
        windata[date] = {'speed':spd,'dir':dir,'lats':lats,'lons':lons}
    return windata

################################
# ADD RECORDS TO TBLWIND 
################################
def push_windata(windata,srcid):

    session = DBman.startSession()
    for date in windata.keys():

        # parse dictionary
        lats = windata[date]['lats']
        lons = windata[date]['lons']
        spd = windata[date]['speed']
        dir = windata[date]['dir']
        
        # add records to tblwind
        for i in range(lats.shape[0]):
            for j in range(lats.shape[1]): 
                loc = WKTSpatialElement('POINT('+str(lons[i][j])+' '+str(lats[i][j])+')')
                record = wind(
                winSourceID=srcid, 
                winLocation=loc, 
                winDateTime=date, 
                winSpeed=float(spd[i][j]), 
                winDirection=float(dir[i][j]))
            session.add(record)    
      
    # commit and close session
    session.commit()
    session.close() 
    session.bind.dispose()
    return 
    
################################
# GENERATE A NAM12 URL STRING
################################
def nam12_url(date,north,south,east,west):
    str = ''.join([ 
        'http://nomads.ncdc.noaa.gov/thredds/ncss/grid/nam218/',
        date.strftime("%Y%m/%Y%m%d/"),
        'nam_218_',
        date.strftime("%Y%m%d"),
        '_0000_000.grb?spatial=bb',
        '&north=',north,'&south=',south,
        '&east=',east,'&west=',west,
        '&temporal=all&addLatLon=true',
        '&var=u_wind_height_above_ground',
        '&var=v_wind_height_above_ground'])
    return str         
   
################################
# STRING TOGETHER WIND-RELATED SUBROUTINES 
################################
def getWIND(config):                     

  north=config['north']
  south=config['south']
  east=config['east']
  west=config['west']
  starttime=config['starttime']
  simduration=config['simduration']
  steeringinterval=config['steeringinterval']
  tmpdir=config['tmpdir']
  wintype=config['wintype']
  
  # PARSE DATE PARAMATERS
  steeringtimes = CMSman.maketimes(starttime,simduration,steeringinterval)
  
  # ADD RECORD TO TBLSOURCETYPE
  srctypeid = add_sourcetype(wintype)    
  
  # DOWNLOAD AND PUSH TO DATABASE
  if wintype=='NAM12': 
      
      # RETRIEVE NAM12 DATA FROM WEB
      windata = getNAM12(steeringtimes,north,south,east,west,tmpdir)
      
      # CHECK IF DATA MATCHES STEERINGTIMES
      wintimes = array(windata.keys())
      for mytime in steeringtimes:
          if (not any(wintimes == mytime)):
              quit('\nERROR: no nam12 data available for time:'+str(mytime))

      # ADD NEW SOURCE TO DATABASE
      srcid = add_source(srctypeid,steeringtimes[0])

      # ADD WIND-DATA TO DATABASE
      push_windata(windata,srcid)
  
  else: quit('oops, i can only support wintype=NAM12')
  return

################################
# STRING TOGETHER WAVE-RELATED SUBROUTINES 
################################
def getWAVE(config):
    
    starttime=config['starttime']
    simduration=config['simduration']
    steeringinterval=config['steeringinterval']
    tmpdir=config['tmpdir']
    wavtype=config['wavtype']
    wavregion=config['wavregion']

    # PARSE DATE PARAMATERS
    steeringtimes = CMSman.maketimes(starttime,simduration,steeringinterval)
    
    # ADD RECORD TO TBLSOURCETYPE
    srctypeid = add_sourcetype(wavtype)
     
    # DOWNLOAD AND PUSH TO DATABASE
    if (wavtype == 'WW3'):
        # RETREIVE WW3 DATA FROM WEB
        wavdata = getWW3(wavregion,tmpdir)
        
        # CHECK IF DATA MATCHES STEERINGTIMES
        wavtimes = array(wavdata.values()[0].keys()) 
        for mytime in steeringtimes:
            if (not any(wavtimes == mytime)):
                quit('\nERROR: no ww3 data available for time:'+str(mytime))
        
        # ADD NEW SOURCE TO DATABASE
        srcid = add_source(srctypeid,steeringtimes[0])
        
        # ADD SPECTRAL-BINS TO DATABASE 
        loc = sort(wavdata.keys())[0]
        date = sort(wavdata[loc].keys())[0]
        freqs = wavdata[loc][date]['freqs']
        dirs = wavdata[loc][date]['dirs']
        specbinid = add_spectrabin(freqs,dirs)

        # ADD SPECTRAL-DATA TO DATABASE        
        push_wavdata(wavdata,srcid,specbinid)

    else: quit('oops, i can only support wavtype=WW3')
    return

################################
# EXECUTABLE SECTION
################################
if __name__ == '__main__':

    # PARSE COMMAND LINE ARGUMENTS
    if len(sys.argv) < 10:
        print '\n... using cmsconfig parameters ...\n'
        config = CMSconfig
    else:
        config = {
        'north':sys.argv[1],
        'south':sys.argv[2],
        'east':sys.argv[3],
        'west':sys.argv[4],
        'starttime':sys.argv[5],
        'simduration':sys.argv[6],
        'steeringinterval':sys.argv[7],
        'tmpdir':sys.argv[8],
        'wintype':sys.argv[9],
        'wavtype':sys.argv[10], 
        'wavregion':sys.argv[11] }
                            
    # DOWNLOAD DATA AND PUSH TO DATABASE 
    getWAVE(config) 
    getWIND(config)

