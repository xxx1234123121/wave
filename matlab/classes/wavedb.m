classdef wavedb
    %WAVEDB Database layer specifically for interacting with the wave
    %database
    %
    %   Detailed explanation goes here
    
    properties
        con;        % database connection handle
        
    end
    
    methods
        function db = wavedb(dbconfig)
            db.con = database(dbconfig.database,dbconfig.username,...
                dbconfig.password,dbconfig.jdbcDriver,dbconfig.driverURL);
            setdbprefs('DataReturnFormat','structure');
        end
        function spec = selectSpectra(db,source,tBegin,tEnd,location)
            if(nargin==1)
                rawspec = fetch(db.con,strcat('SELECT  ',...
                    '  tblwave.wavdatetime,         ',...
                    '  tblwave.wavspectra,          ',...
                    '  tblwave.wavheight,           ',...
                    '  tblwave.wavpeakdir,          ',...
                    '  tblwave.wavpeakperiod,       ',...
                    '  ST_X(tblwave.wavlocation),   ',...
                    '  ST_Y(tblwave.wavlocation),   ',...
                    '  tblspectrabin.spcfreq,       ',...
                    '  tblspectrabin.spcdir,        ',...
                    '  tblsource.srcname,           ',...
                    '  tblsource.srcconfig,         ',...
                    '  tblsource.srcbeginexecution, ',...
                    '  tblsource.srcendexecution,   ',...
                    '  tblsource.srcsourcetypeid    ',...
                    ' FROM ',...
                    '  public.tblwave, ',...
                    '  public.tblspectrabin, ',...
                    '  public.tblsource ',...
                    ' WHERE ',...
                    '  tblwave.wavspectrabinid = tblspectrabin.spcid AND ',...
                    '  tblwave.wavsourceid = tblsource.srcid'));
                n = size(rawspec.st_x,1);
                spec(n) = spectra;
                for i=1:n                   
                    spec(i) = spectra(rawspec.wavdatetime(i),...
                        [rawspec.st_x(i),rawspec.st_y(i)],...
                        double(rawspec.wavspectra{i}.getArray()),...
                        double(rawspec.spcfreq{i}.getArray()),...
                        double(rawspec.spcdir{i}.getArray()));
                end
                
            else
                con = source + tBegin + tEnd +location;
            end
        end
    end 
end

