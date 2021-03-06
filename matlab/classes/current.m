classdef current
    %CURRENT A class for representing ocean currents
    %   Detailed explanation goes here
    
    properties
        % SOURCE NAME
        srcName;    % refers to the source name in the database
        
        % TIME AND LOCATION
        datetime;   % datenum
        location;   % x,y Lon/Lat coordinates
        
        % VELOCITY
        speed;      % the 1D or 2D matrix of spectral values
        dir;        % frequency bins
        
        % UNITS
        speedUnits;     % choices: 'm/s','mph','kt'
        dirUnits;       % choices: 'deg','rad'
        
    end
    
    methods
        function cur = current(sourceName,datetime,location,s,d,sUnits,dUnits)
            if(nargin>0)
                cur.srcName = sourceName;
                if(length(char(datetime))>19)
                    datetime = substr(char(datetime),1,19);
                end
                cur.datetime   = datenum(datetime,'yyyy-mm-dd HH:MM:SS');
                cur.location   = location;
                cur.speed      = s;
                cur.dir        = d;
                cur.speedUnits = sUnits;
                cur.dirUnits   = dUnits;
            end
        end
        function x = getX(cur)
            x = cur.location(1);
        end
        function y = getY(cur)
            y = cur.location(2);
        end
        function d = getDatetime(cur)
            d = cur.datetime;
        end
        function src = getSourceName(cur)
            src = cur.srcName;
        end
        function sp = get.speed(cur)
            sp  = cur.speed;
        end
        function dir = get.dir(cur)
            dir = cur.dir;
        end
    end
end

