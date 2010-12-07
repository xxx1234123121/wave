classdef spectra
    %SPECTRA A class for representing one or two dimensional surface wave
    %spectra.
    %   Detailed explanation goes here
    
    properties
        % TIME AND LOCATION
        datetime;   % datenum
        location;   % x,y Lon/Lat coordinates
        
        % SPECTRA
        spec;       % the 1D or 2D matrix of spectral values
        freqBin;    % frequency bins
        dirBin;     % direction bins, leave as NULL if 1D
        
        % BULK STATISTICS
        hs;         % significant wave height
        tp;         % peak period
        te;         % energy period
    end
    
    methods
        function spec = spectra(datetime,location,sp,freqBin,dirBin)
            if(nargin>0)
                spec.datetime   = datenum(datetime,'yyyy-mm-dd HH:MM:SS');
                spec.location   = location;
                spec.spec       = sp;
                spec.freqBin    = freqBin;
                if nargin>4,spec.dirBin = dirBin; end
            end
        end
        function x = getX(spec)
            x = spec.location(1);
        end
        function y = getY(spec)
            y = spec.location(2);
        end
        function d = getDatetime(spec)
            d = spec.datetime;
        end
    end    
end

