################################
# IMPORT MODULES
################################
import datetime #posix support
import glob #file wildcard support
import re #regex support
from numpy import * #math support
from os import path,system,remove
strptime = datetime.datetime.strptime

################################
# IMPORT DATABASE FUNCTIONS
################################
import DBman
from config import DBconfig

################################
# IMPORT CONSTANTS
################################
#from config import CMSconfig
### #cmsdir = '/Users/naftali/Desktop/CMS/bin'
### #simfile = 'WAVE.sim'
### #depfile = 'WAVE.dep'
### #cardfile = 'FLOW.cmcards'
### #nestfn = 'nest.dat'
### #metafn = 'nest.meta'
### #windfile = 'wind.dat'
### #steeringinterval = 6 #hours
### 
### ################################
### # DETERMINE SPATIAL DOMAIN
### ################################
### def spatialdomain(cmsdir,simfile,depfile):
###   #get origin
###   simfile = glob.glob(cmsdir + '/' + simfile)[0]
###   lines = open(simfile).read()
###   pat = re.compile("(-*\d+\.*\d*)")
###   match = pat.findall(lines)
###   lon_ll = float(match[0])
###   lat_ll = float(match[1])
###   #get grid size
###   depfile = glob.glob(cmsdir + '/' + depfile)[0]
###   lines = open(depfile).read()
###   pat = re.compile(".*?(\d+\.*\d*)")
###   match = pat.findall(lines)
###   nx = int(match[0])
###   ny = int(match[1])
###   delta_x = float(match[2])
###   delta_y = float(match[3])
###   #calculate ur corner
###   lon_ur = lon_ll + (nx-1)*delta_x
###   lat_ur = lat_ll + (ny-1)*delta_y
###   #create box2d object
###   point_ll = 'ST_SETSRID(ST_POINT('+str(lon_ll)+','+str(lat_ll)+'),32610)'
###   point_ur = 'ST_SETSRID(ST_POINT('+str(lon_ur)+','+str(lat_ur)+'),32610)'
###   box = 'ST_SETSRID(ST_MAKEBOX2D('+point_ll+','+point_ur+'),32610)'
###   #create coordinate arrays
###   gridx = [[lon_ll+(i-1)*delta_x for i in range(nx)] for j in range(ny)]
###   gridy = [[lat_ll+(j-1)*delta_y for i in range(nx)] for j in range(ny)]
###   return [box,gridx,gridy]
### 
### ################################
### # DETERMINE TEMPORAL DOMAIN
### ################################
### def temporaldomain(cmsdir,cardfile,steeringinterval):
###   cardfile = glob.glob(cmsdir + '/' + cardfile)[0]
###   lines = open(cardfile).read()
###   pat1 = re.compile("STARTING_JDATE.*?(\d{8})")
###   pat2 = re.compile("STARTING_JDATE_HOUR.*?(\d+)")
###   pat3 = re.compile("DURATION_RUN.*?(\d+)")
###   startdy = pat1.findall(lines)[0]
###   starthr = pat2.findall(lines)[0]
###   durationrun = pat3.findall(lines)[0]
###   durationrun = float(durationrun)
###   durationrun = datetime.timedelta(durationrun/24.0)
###   steeringinterval = datetime.timedelta(steeringinterval/24.0)
###   starttime = startdy + starthr
###   starttime = strptime( starttime, '%Y%m%d%H' )
###   stoptime = starttime + durationrun
###   steeringtimes = []
###   mytime = starttime
###   while( mytime <= stoptime):
###     steeringtimes.append(mytime)
###     mytime = mytime+steeringinterval
###   starttime = starttime.strftime('%Y%m%d %H:00' )
###   stoptime = stoptime.strftime('%Y%m%d %H:00' )
###   starttime = '(TIMESTAMP \''+starttime+'\')'
###   stoptime = '(TIMESTAMP \''+stoptime+'\')'
###   return [starttime,stoptime,steeringtimes]
### 
### ################################
### # RETREIVE DATA FROM TBLWAVE
### ################################
### def getwavedata(DBconfig,starttime,stoptime,box):
###   spec,specid,wavtime,wavloc,wavx,wavy = [[],[],[],[],[],[]]
###   session = DBman.startSession( DBconfig )
###   q1 = ' select wavid from tblwave where ST_WITHIN('
###   q2 = ' ST_TRANSFORM(wavlocation,32610),' + box + ') '
###   q3 = ' and wavdatetime>='+starttime
###   q4 = ' and wavdatetime<='+stoptime
###   q5 = q1+q2+q3+q4
###   q6 = ' select wavspectra,wavspectraid,'
###   q7 = ' wavdatetime,wavlocation,'
###   q8 = ' ST_X(ST_TRANSFORM(wavlocation,32610)),'
###   q9 = ' ST_Y(ST_TRANSFORM(wavlocation,32610)) '
###   q10 = 'from tblwave where wavid in ('+q5+')'
###   q11 = q6+q7+q8+q9+q10
###   result = session.execute(q11).fetchall()
###   for k in range(len(result)):
###     spec.append(result[k][0])
###     specid.append(result[k][1])
###     wavtime.append(result[k][2])
###     wavloc.append(result[k][3])
###     wavx.append(result[k][4])
###     wavy.append(result[k][5])
###   spec=array(spec)
###   specid=array(specid)
###   wavtime=array(wavtime)
###   wavloc=array(wavloc)
###   wavx=array(wavx)
###   wavy=array(wavy)
###   # RETREIVE FREQ/DIR BINS
###   freq,dir = [[],[]]
###   for myspectraid in specid:
###     q1 = "select spectrafreq,spectradir from "
###     q2 = "tblspectra where spectraid='"+myspectraid+"'"
###     q3 = q1+q2
###     result = session.execute(q3).fetchall()
###     freq.append(result[0][0])
###     dir.append(result[0][1])
###   freq=array(freq)
###   dir=array(dir)
###   session.close()
###   return [spec,specid,wavtime,wavloc,wavx,wavy,freq,dir]
### 
### ################################
### # RETREIVE DATA FROM TBLWIND
### ################################
### def getwinddata(DBconfig,starttime,stoptime):
###   winspeed, windir, winid, wintime, winx, winy = [[],[],[],[],[],[]]
###   session = DBman.startSession( DBconfig )
###   q1 = ' select winid from tblwind where'
###   q2 = ' windatetime>='+starttime
###   q3 = ' and windatetime<='+stoptime
###   q4 = q1+q2+q3
###   q5 = ' select winspeed,windirection,windatetime,'
###   q6 = ' ST_X(ST_TRANSFORM(winlocation,32610)),'
###   q7 = ' ST_Y(ST_TRANSFORM(winlocation,32610)) '
###   q8 = 'from tblwind where winid in ('+q4+')'
###   q9 = q5+q6+q7+q8
###   result = session.execute(q9).fetchall()
###   for k in range(len(result)):
###     winspeed.append(result[k][0])
###     windir.append(result[k][1])
###     wintime.append(result[k][2])
###     winx.append(result[k][3])
###     winy.append(result[k][4])
###   winspeed=array(winspeed)
###   windir=array(windir)
###   wintime=array(wintime)
###   winx=array(winx)
###   winy=array(winy)
###   return [winspeed,windir,wintime,winx,winy]
