classdef spectra
    %SPECTRA A class for representing one or two dimensional surface wave
    %spectra.
    %   Detailed explanation goes here
    
    properties
        % TIME AND LOCATION
        datetime;   % datevec
        location;   % x,y Lat/Lon coordinates
        
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
        function spec = spectra(datetime,location,sp,freqbin,dirbin)
            if(nargin>0)
                spec.datetime   = datevec(datetime,'yyyy-mm-dd HH:MM:SS');
                spec.location   = location;
                spec.spec       = sp;
                spec.freqbin    = freqbin;
                if nargin>4,spec.dirbin = dirbin; end
            end
        end
    end
    
end

