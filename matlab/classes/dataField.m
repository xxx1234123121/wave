classdef dataField
    
    properties
        boundingBox;        % [x,y,t] where row 1 is UR and row 2 is LL
        % t(1) is beginning and t(2) is ending
        X;      % X,Y,T are arrays of coordinates, T is an array of datenum
        Y;
        T;
        Z;      % Z represents an array of objects which contain the state
        % variable(s) being represented
        isStructuredGrid;    % boolean
        classOfZ;            % the class of the objects in Z
    end
    methods
        function df = dataField(Z,X,Y,T)
            df.classOfZ = class(Z);
            if nargin==1
                if strcmp(df.classOfZ,'spectra')==1
                    n = size(Z,2);
                    df.X = zeros(n,1);
                    df.Y = zeros(n,1);
                    df.T = zeros(n,1);
                    for i=1:n
                        df.X(i) = Z(i).getX();
                        df.Y(i) = Z(i).getY();
                        df.T(i) = Z(i).getDatetime();
                    end
                    df.Z = Z;
                end
            else if nargin == 4
                    df.X = X;
                    df.Y = Y;
                    df.T = T;
                    df.Z = Z;
                end
            end
            
            df.boundingBox = [ max(df.X), max(df.Y), max(df.T);
                min(df.X), min(df.Y), min(df.T) ];
        end
        
        function plotPointSpec(df,t,x,y,collapse)
            if strcmp(df.classOfZ,'spectra')==0
                error(strcat('Cannot plot point spectra for data of class '...
                    ,df.classOfZ))
            end
            
            if(nargin<5)
                collapse = false;
            end
            if(nargin<4)
                y = df.Y(1);
            end
            if(nargin<3)
                x = df.X(1);
            end
            if(nargin<2)
                t = df.T(1);
            end
            
            % find the point closest to x,y,t in Euclidean space
            iNearby = knnsearch([x,y,t],[df.X df.Y,df.T]);
            
            if(collapse || ndims(df.Z(iNearby).spec)==1)
                if(ndims(df.Z(iNearby).spec)==2)
                    plot(df.Z(iNearby).freqBin,sum(df.Z(iNearby).spec));
                else
                    plot(df.Z(iNearby).freqBin,df.Z(iNearby).spec);
                end
                set(gcf(),'Color','White');
                set(gca(),'Position',get(gca(),'Position')+[0,0,0,-.1]);
                
                title({'Spectral Density',strcat('[',...
                    locationLabel(df.Y(iNearby),df.X(iNearby),...
                    df.T(iNearby)),']')},...
                    'FontWeight','bold','Units','normalized',...
                    'Position',[0.5,1.2,0]...
                    );
                
                xlabel('Frequency (Hz)');
                ylabel('Density (m^2/Hz)');
                addtxaxis(gca(),'1./x',1./get(gca(),'XTick'),'Period (s)');
            else
                h = mypolar([0 2*pi], [0 max(df.Z(iNearby).freqBin)]);
                title({'Directional Spectral Density',strcat('[',...
                    locationLabel(df.Y(iNearby),df.X(iNearby),...
                    df.T(iNearby)),']')},...
                    'FontWeight','bold','Units','normalized'...
                    );
                delete(h);
                hold on;
                polarcont(df.Z(iNearby).freqBin,metToMathAngle(df.Z(iNearby).dirBin),df.Z(iNearby).spec');
                cb = colorbar;
                xlabel('Radius = Frequency (Hz)');
                set(get(cb,'ylabel'),'String','Density (m^2/Hz)');
                hold off;
                
            end
            
        end
        
    end
end
