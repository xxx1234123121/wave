classdef wind
    %WIND A class for representing wind velocity
    %   Detailed explanation goes here
    
    properties
        % SOURCE NAME
        srcName;    % refers to the source name in the database
        
        % TIME AND LOCATION
        datetime;   % datenum
        location;   % x,y Lon/Lat coordinates
        
        % VELOCITY
        speed;       % the 1D or 2D matrix of spectral values
        dir;    % frequency bins
        
        % UNITS
        speedUnits;     % choices: 'm/s','mph','kt'
        dirUnits;       % choices: 'deg','rad'
    end
    
    methods
        function win = wind(sourceName,datetime,location,s,d,sUnits,dUnits)
            if(nargin>0)
                win.srcName = sourceName;
                if(length(char(datetime))==19)
                    win.datetime   = datenum(datetime,'yyyy-mm-dd HH:MM:SS');
                elseif(length(char(datetime))==21)
                    win.datetime   = datenum(datetime,'yyyy-mm-dd HH:MM:SS.0');
                end
                win.location   = location;
                win.speed      = s;
                win.dir        = d;
                win.speedUnits = sUnits;
                win.dirUnits   = dUnits;
            end
        end
        function x = getX(win)
            x = win.location(1);
        end
        function y = getY(win)
            y = win.location(2);
        end
        function d = getDatetime(win)
            d = win.datetime;
        end
        function src = getSourceName(win)
            src = win.srcName;
        end
        function sp = get.speed(win)
            sp = win.speed;
        end
        function dr = get.dir(win)
            dr = win.dir;
        end
    end
end

