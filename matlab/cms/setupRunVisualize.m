%% Connect to db
config = waveConfig('../config/dbconfig.json')
db = waveDB(config.db)

%% Pull spectral data from Buoy 46022 for a 6 hour time period
buoySrc = 'NDBC-46022';
tBegin  = datenum('2009-12-02 00:00:00','yyyy-mm-dd HH:MM:SS');
tEnd    = datenum('2009-12-02 05:59:59','yyyy-mm-dd HH:MM:SS'); % the range is inclusive

spec = db.selectSpectra(buoySrc,tBegin,tEnd); % spec is a dataField object

%% Plot the directional spectra and the one dimensional spectra

% 2D spectra for the record at 3am, located at the buoy
spec.plotPointSpec(datenum('2009-12-02 03:00:00','yyyy-mm-dd HH:MM:SS'),...
    spec.X(1),spec.Y(1));

% 1D spectra for same conditions as above
spec.plotPointSpec(datenum('2009-12-02 03:00:00','yyyy-mm-dd HH:MM:SS'),...
    spec.X(1),spec.Y(1),true);