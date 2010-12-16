classdef dataField
    
    properties
        boundingBox;        % an object of class 'extent'
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
                if (strcmp(df.classOfZ,'spectra')==1 || ...
                        strcmp(df.classOfZ,'wind')==1 || ...
                        strcmp(df.classOfZ,'current')==1)
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
            else if nargin == 5
                    df.X = X;
                    df.Y = Y;
                    df.T = T;
                    df.Z = Z;
                end
            end
            
            df.boundingBox = extent(min(df.T),max(df.T),...
                [min(df.X),min(df.Y)],...
                [max(df.X),max(df.Y)]);
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
                
                title({['Spectral Density -- ',char(df.Z(iNearby).getSourceName)],...
                    strcat('[',locationLabel(df.Y(iNearby),df.X(iNearby),...
                    df.T(iNearby)),']')},...
                    'FontWeight','bold','Units','normalized',...
                    'Position',[0.5,1.2,0]...
                    );
                
                xlabel('Frequency (Hz)');
                ylabel('Density (m^2/Hz)');
                addtxaxis(gca(),'1./x',1./get(gca(),'XTick'),'Period (s)');
            else
                h = mypolar([0 2*pi], [0 max(df.Z(iNearby).freqBin)]);
                title({['Directional Spectral Density -- ',char(df.Z(iNearby).getSourceName)],...
                    strcat('[',locationLabel(df.Y(iNearby),df.X(iNearby),...
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
        
        function plotContour(df,fieldName,cropExtent)
            if(nargin<2)
                error('Must specify a fieldName (e.g. for a datafield with spectra objects you can specify ''Hs''');
            end
            if(nargin<3)
                cropExtent = df.boundingBox;
                %%% for now, just constraint it to the first time step
                cropExtent.te = cropExtent.tb;
            end
            inds = df.isInCropExtent(cropExtent);
            toplot = zeros(size(inds,1),3);
            for i=1:size(inds,1)
                toplot(i,:) = [df.X(inds(i)),df.Y(inds(i)),...
                    getfield(df.Z(inds(i)),fieldName)];
            end
            contour(toplot(:,1),toplot(:,2),tplot(:,3));
        end
        
        function inds = isInCropExtent(df,cropExtent)
            logicalSum = sum( [df.T >= cropExtent.getTimeBegin(), ...
                df.T <= cropExtent.getTimeEnd(), ...
                df.X >= cropExtent.getXMin(), ...
                df.X <= cropExtent.getXMax(), ...
                df.Y >= cropExtent.getYMin(), ...
                df.Y <= cropExtent.getYMax()], 2 );
            inds = find(logicalSum == 6);
        end
    end
end
