classdef spectra
    %SPECTRA A class for representing one or two dimensional surface wave
    %spectra.
    %   Detailed explanation goes here
    
    properties
        % TIME AND LOCATION
        datetime;   % datevec
        location;   % x,y GIS coordinates
        projection; % associated GIS projection
        
        % SPECTRA
        spec;       % the 1D or 2D matrix of spectral values
        freqbin;    % frequency bins
        dirbin;     % direction bins, leave as NULL if 1D
        
        % BULK STATISTICS
        hs;         % significant wave height
        tp;         % peak period
        te;         % energy period
    end
    
    methods
        function spec = spectra(datetime,location,projection,spec,...
            freqbin,dirbin)
            spec.datetime   = datevec(datetime,'yyyy-mm-dd HH:MM:SS');
            spec.location   = location;
            spec.projection = projection;
            spec.freqbin    = freqbin;
            if nargin<5,spec.dirbin = dirbin; end
        end
    end
    
end

