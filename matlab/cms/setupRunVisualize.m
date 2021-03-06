%% Connect to db
config = waveConfig('../config/dbconfig.json');
db = waveDB(config.db);

%% Pull spectral data from Buoy 46022 for a 6 hour time period
buoySrc = 'NDBC-46022';
tBegin  = datenum('2009-10-20 00:00:00','yyyy-mm-dd HH:MM:SS');
tEnd    = datenum('2009-10-22 00:00:00','yyyy-mm-dd HH:MM:SS'); % the range is inclusive

spec = db.selectSpectra(buoySrc,tBegin,tEnd); % spec is a dataField object

%% Plot the directional spectra and the one dimensional spectra

% 2D spectra for the record at 3am, located at the buoy
spec.plotPointSpec(datenum('2009-12-02 03:00:00','yyyy-mm-dd HH:MM:SS'),...
    datenum('2009-12-02 03:00:00','yyyy-mm-dd HH:MM:SS'),...
    spec.X(1),spec.Y(1));

% 1D spectra for same conditions as above
figure;
spec.plotPointSpec(datenum('2009-12-02 03:00:00','yyyy-mm-dd HH:MM:SS'),...
    datenum('2009-12-02 03:00:00','yyyy-mm-dd HH:MM:SS'),...
    spec.X(1),spec.Y(1),true);

% Animation of 2D spectra for the buoy
figure;
M = spec.plotPointSpec(datenum('2009-10-20 00:00:00','yyyy-mm-dd HH:MM:SS'),...
    datenum('2009-10-22 00:00:00','yyyy-mm-dd HH:MM:SS'),...
    spec.X(1),spec.Y(1));
movie(M,1,2);

% Save the animation to an mpg formatted file
vidObj = VideoWriter('animated-buoy-spectra');
vidObj.FrameRate = 3;
open(vidObj);
writeVideo(vidObj,M);
close(vidObj);

% Animation of 1D spectra for the record at 12-5am, located at the buoy
figure;
M = spec.plotPointSpec(datenum('2009-12-02 00:00:00','yyyy-mm-dd HH:MM:SS'),...
    datenum('2009-12-02 05:00:00','yyyy-mm-dd HH:MM:SS'),...
    spec.X(1),spec.Y(1),true);
movie(M,1,2);

%% Pull wind data from Buoy 46022 for the same time period as above
win = db.selectWind(buoySrc,tBegin,tEnd);

%% Pull current data from HFRadar station for available time period
hfradarSrc = 'HFRadar-6km';
tBegin  = datenum('2010-12-12 01:00:00','yyyy-mm-dd HH:MM:SS');
tEnd    = datenum('2010-12-12 06:59:59','yyyy-mm-dd HH:MM:SS');

cur = db.selectCurrent(hfradarSrc,tBegin,tEnd);

%% Plot a contour and a surface of the current speed
cur.plotContour('speed');
cur.plotSurf('speed',extent(cur.T(1),cur.T(1),[39,-125],[39.5,-124.5]));

%% Pull spectra data from WWIII output
www3Src = 'WWIII_20101221_00';
tBegin  = datenum('2010-12-21 00:00:00','yyyy-mm-dd HH:MM:SS');
tEnd    = datenum('2010-12-21 23:59:59','yyyy-mm-dd HH:MM:SS');
w3 = db.selectSpectra(www3Src,tBegin,tEnd);


%% Pull spectra data from humboldt-example CMS run
cmsSrc = 'humboldt-example-humboldt-example';
tBegin  = datenum('2010-12-28 04:00:00','yyyy-mm-dd HH:MM:SS');
tEnd    = datenum('2010-12-28 04:59:59','yyyy-mm-dd HH:MM:SS');
%cms = db.selectSpectra(cmsSrc,tBegin,tEnd);
cms = db.selectCurrent(cmsSrc,tBegin,tEnd);

cmsSrc = 'HT-V6__Tel-Flow-Linux';
tBegin  = datenum('2007-12-01 00:00:00','yyyy-mm-dd HH:MM:SS');
tEnd    = datenum('2007-12-02 00:00:00','yyyy-mm-dd HH:MM:SS');
%cms = db.selectSpectra(cmsSrc,tBegin,tEnd);
cms = db.selectCurrent(cmsSrc,tBegin,tEnd);
humBegin  = datenum('2007-12-01 17:00:00','yyyy-mm-dd HH:MM:SS');
humEnd    = datenum('2007-12-01 17:59:00','yyyy-mm-dd HH:MM:SS');
humBox = extent(humBegin,humEnd,cms.boundingBox.ll,cms.boundingBox.ur);
cms.plotField('quiver','blah',humBox);
colorbar;

%% Pull wind data from NAM12
namSrc = 'NAM12_20101229_00_0';
tBegin  = datenum('2010-12-29 00:00:00','yyyy-mm-dd HH:MM:SS');
tEnd    = datenum('2010-12-29 06:59:59','yyyy-mm-dd HH:MM:SS');
nam = db.selectWind(namSrc,tBegin,tEnd);
humBox = extent(tBegin,tBegin,[-120.48,38],[-117,42]);
nam.plotField('quiver','blah',humBox);
