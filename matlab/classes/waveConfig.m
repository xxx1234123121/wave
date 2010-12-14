classdef waveConfig
    %WAVECONFIG Class to organize configurations for the wave software
    %   Detailed explanation goes here
    
    properties
        db;         % Database config directives
    end
    
    methods
        function config = waveConfig(configPath)
            fid = fopen(configPath);
            s = fscanf(fid,'%c');
            st = parse_json(s);
            config.db = st{1};
        end
    end
    
end

