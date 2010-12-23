classdef extent
    %EXTENT Class for storing the spatial and temporal extents of a data
    %field.
    %   Detailed explanation goes here
    
    properties
        tb; % begin date as datenu
        te; % end date as datenum
        ll; % lower left coords (x,y)
        ur; % upper right coords (x,y)
    end
    
    methods
        function ext=extent(tbIN,teIN,llIN,urIN)
            ext.tb = tbIN;
            ext.te = teIN;
            ext.ll = llIN;
            ext.ur = urIN;
        end
        function tb = getTimeBegin(ext)
            tb = ext.tb;
        end
        function te = getTimeEnd(ext)
            te = ext.te;
        end
        function xmin = getXMin(ext)
            xmin = ext.ll(1);
        end
        function xmax = getXMax(ext)
            xmax = ext.ur(1);
        end
        function ymin = getYMin(ext)
            ymin = ext.ll(2);
        end
        function ymin = getYMax(ext)
            ymin = ext.ur(2);
        end
        function setTimeBegin(ext,tbIN)
            ext.tb = tbIN;
        end
        function setTimeEnd(ext,teIN)
            ext.te = teIN;
        end
    end
    
end

