classdef spectra
    %SPECTRA A class for representing one or two dimensional surface wave
    %spectra.
    %   Detailed explanation goes here
    
    properties
        % SOURCE NAME
        srcName;    % refers to the source name in the database
        
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
        function spec = spectra(sourceName,datetime,location,sp,...
                freqBin,dirBin)
            if(nargin>0)
                if(length(char(datetime))==19)
                    spec.datetime   = datenum(datetime,'yyyy-mm-dd HH:MM:SS');
                elseif(length(char(datetime))==21)
                    spec.datetime   = datenum(datetime,'yyyy-mm-dd HH:MM:SS.0');
                end
                spec.location   = location;
                spec.spec       = sp;
                spec.freqBin    = freqBin;
                spec.srcName    = sourceName;
                if nargin>5
                    spec.dirBin = dirBin;
                end
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
        function src = getSourceName(spec)
            src = spec.srcName;
        end
        function hs = get.hs(spec)
            if(size(spec.hs,1)==0)
                spec.hs = 4*sqrt(spec.nthMoment(0));
            end
            hs = spec.hs;
        end
        function tp = get.tp(spec)
            if(size(spec.tp,1)==0)
                if(size(spec.dirBin,1)>0)
                    spec.tp = 1/spec.freqBin(find(sum(spec.spec,2)==max(sum(spec.spec,2))));
                else
                    spec.tp = 1/spec.freqBin(find(spec.spec==max(spec.spec)));
                end
            end
            tp = spec.tp;
        end
        function te = get.te(spec)
            if(size(spec.te,1)==0)
               spec.te = spec.nthMoment(-1)/spec.nthMoment(0);
            end
            te = spec.te;
        end
        function m = nthMoment(spec,n)
            if(nargin==1)n=0;end
            if(size(spec.dirBin,2)>0)
                m = simprule((spec.freqBin.^n).*sum(spec.spec,2),NaN,spec.freqBin);
            else
                m = simprule((spec.freqBin.^n).*spec.spec,NaN,spec.freqBin);
            end
        end
    end
end

