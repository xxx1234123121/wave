#!/usr/bin/env python2.7
#SEE BELOW FOR COMMAND LINE ARGUMENTS
#EXAMPLE CALL: python getNAM12Wind.py 50 35 -120 -130 2010/12/22 2011/12/23 ~/Desktop/tmp

#next update: use this server instead...can specify spatial bounding box to reduce download time
#http://nomads.ncdc.noaa.gov/thredds/ncss/grid/nam218/201012/20101220/
#nam_218_20101220_0000_000.grb/dataset.html?spatial=bb&
#north=50&west=-130&east=-120&south=35&temporal=all&addLatLon=true&var=u_wind_height_above_ground

################################
# IMPORT MODULES 
################################
import urllib #web support
import datetime #posix support
from PyNIO import Nio #grib support
import sys #argument parsing
from geoalchemy import WKTSpatialElement
from numpy import * #math support
from math import * #pi constant

################################
# IMPORT DATABASE FUNCTIONS
################################
from os import path,system
DBman_path = path.abspath('.')+'/../lib/'
sys.path.insert( 0, DBman_path )
from wavecon import DBman

################################
# PARSE COMMAND LINE ARGUMENTS
################################
north =      sys.argv[1]       #50
south =      sys.argv[2]       #35
east =       sys.argv[3]       #-120
west =       sys.argv[4]       #-130
starttime =  sys.argv[5]       #YYYY/MM/DD
stoptime =   sys.argv[6]       #YYYY/MM/DD
tmpdir =     sys.argv[7]       #/Users/naftali/Desktop/tmp

################################
# PARSE DATE PARAMATERS
################################
starttime = datetime.datetime.strptime( starttime, '%Y/%m/%d' )
stoptime = datetime.datetime.strptime( stoptime, '%Y/%m/%d' )
delta = datetime.timedelta(.25) # 6 hour increment
if (stoptime==starttime):
  stoptime=starttime+datetime.timedelta(1)

################################
# FILENAME PARAMETERS
################################
tmpfile = tmpdir + '/tmp.grb'
baseurl = 'http://nomads.ncdc.noaa.gov/data/namanl/'
filename1 = 'namanl_218_'
filename2 = '_000.grb'

################################
# CREATE DATABASE OBJECTS
################################
srctype = DBman.accessTable( None, 'tblsourcetype' )
src = DBman.accessTable( None, 'tblsource')
wind = DBman.accessTable( None, 'tblwind' ) 

################################
# ADD NAM12 TO tblSourceType
################################
session = DBman.startSession()     
srctypename = 'NAM12'
existing = session.query(srctype)\
    .filter( srctype.sourcetypename == srctypename )
if ( existing.first() == None ):
    record = srctype(srctypename)                              
    session.add(record)
    session.commit()
srctypeid = session.query(srctype)\
    .filter( srctype.sourcetypename == srctypename )\
    .first().id
session.close()
session.bind.dispose()

################################
# GET DATA FOR EACH TIMESTAMP
################################
date = starttime
while date < stoptime :

    # build url string and download file, re-open as niofile
    url1 = date.strftime("%Y%m/%Y%m%d/")
    url2 = filename1 + date.strftime("%Y%m%d_%H00") + filename2
    url3 = baseurl + url1 + url2 
    print '\n... (NAM12) downloading date: ' + str(date) + ' ...'
    urllib.urlretrieve(url=url3,filename=tmpfile)
    print 'done\n'
    niofile = Nio.open_file(tmpfile) 
    
    # extract latitudes/longitudes
    lats = niofile.variables['gridlat_218'].get_value()
    lons = niofile.variables['gridlon_218'].get_value()
    
    # extract u-component
    niovar = niofile.variables['U_GRD_218_MWSL']
    ugrid = niovar.get_value()  
    
    # extract v-component
    niovar = niofile.variables['V_GRD_218_MWSL']
    vgrid = niovar.get_value()  
          
    # crop to grid
    filter = (lats>=south) & (lats<=north) & (lons>=west) & (lons<=east)
    lats = lats[filter]    
    lons = lons[filter]    
    ugrid = ugrid[filter]    
    vgrid = vgrid[filter]    
    
    # convert from u/v to speed/direction
    # dir = cartesian coordinates, radians
    # (0 = traveling east, 90 = traveling north)     
    spd = (ugrid**2.0 + vgrid**2.0)**(1.0/2.0)
    dir = arctan2(vgrid,ugrid)   
    dir = dir*180./pi 
    
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
    session = DBman.startSession()     
    session.add(record)    
    session.commit()
    srcid = session.query(src)\
        .filter( src.srcname == srcname )\
        .first().id

    # add records to tblwind
    for i in range(len(lats)) : 
        loc = WKTSpatialElement('POINT('+str(lons[i])+' '+str(lats[i])+')')
        record = wind(
            winSourceID=srcid, 
            winLocation=loc, 
            winDateTime=date, 
            winSpeed=float(spd[i]), 
            winDirection=float(dir[i]))
        session.add(record)    
    
    # close session
    session.commit()
    session.close() 
    session.bind.dispose()
    
    # close grb file and delete
    niofile.close()
    system('rm ' + tmpfile) 
    
    # go to next timestamp
    print 'done with: '+str(date)
    date = date + delta
    
### TO DO ###
#modulize
#parallelize loops
