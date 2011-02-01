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
        
        % THE FOLLOWING FIELDS are non-null iff the param 'scalarFields' is
        % passed to the constructor
        scalarFields;     % row cell array containing the name of the scalar
        % quantities that exist in Z
        scalarArrays;     % an M x N matrix containing the scalar quantities extracted
        % from Z for ease of manipulation
        % M is the length of X,Y,T, and Z, and
        % N is the number of scalars to be stored.
        interpFuns;        % contains the result of TriScatteredInterp for each
        % scalard field, used for quick interpolation
    end
    methods
        % scalarFields is a row cell array
        function df = dataField(Z,scalarFieldsIn,X,Y,T)
            df.classOfZ = class(Z);
            if(nargin>0 && nargin<3)
                if (strcmp(df.classOfZ,'spectra')==1 || ...
                        strcmp(df.classOfZ,'wind')==1 || ...
                        strcmp(df.classOfZ,'current')==1)
                    m = size(Z,2);
                    df.X = zeros(m,1);
                    df.Y = zeros(m,1);
                    df.T = zeros(m,1);
                    if(nargin==2)
                        df.scalarFields = scalarFieldsIn;
                        n = size(df.scalarFields,2);
                        df.scalarArrays = zeros(m,n);
                    end
                    for i=1:m
                        df.X(i) = Z(i).getX();
                        df.Y(i) = Z(i).getY();
                        df.T(i) = Z(i).getDatetime();
                        if(nargin==2)
                            for j=1:n
                                express = ['Z(i).',char(df.scalarFields(j))];
                                df.scalarArrays(i,j) = eval(express);
                            end
                        end
                    end
                    df.Z = Z;
                    if(nargin==2)
                        df.interpFuns = cell(n,1);
                        for j=1:n
                            df.interpFuns{j} = TriScatteredInterp(df.X,df.Y,df.T,df.scalarArrays(:,j));
                        end
                    end
                end
            else if nargin == 6
                    df.X = X;
                    df.Y = Y;
                    df.T = T;
                    df.Z = Z;
                end
            end
            if nargin==6
                
            end
            
            df.boundingBox = extent(min(df.T),max(df.T),...
                [min(df.X),min(df.Y)],...
                [max(df.X),max(df.Y)]);
        end
        
        function M = plotPointSpec(df,tb,te,x,y,collapse)
            if strcmp(df.classOfZ,'spectra')==0
                error(strcat('Cannot plot point spectra for data of class '...
                    ,df.classOfZ))
            end
            if(nargin<6)
                collapse = false;
            end
            if(nargin<5)
                y = df.Y(1);
            end
            if(nargin<4)
                x = df.X(1);
            end
            if(nargin<3)
                te = df.T(1);
            end
            if(nargin<2)
                tb = df.T(1);
            end
            
            if(tb~=te)
                tbetween = sort(df.T(df.T >= tb & df.T <= te));
                for i=1:length(tbetween)
                    makePointSpecPlot(df,tbetween(i),x,y,collapse);
                    %axis equal;
                    caxis([0,10]);
                    M(i) = getframe(gcf);
                end
            else
                makePointSpecPlot(df,tb,x,y,collapse);
                M = getframe(gcf);
            end
        end
        
        function makePointSpecPlot(df,t,x,y,collapse)
            clf;
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
                
                title({['Spectral Density -- ',regexprep(char(df.Z(iNearby).getSourceName),'\_','\\_')],...
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
                title({['Directional Spectral Density -- ',regexprep(char(df.Z(iNearby).getSourceName),'\_','\\_')],...
                    strcat('[',locationLabel(df.Y(iNearby),df.X(iNearby),...
                    df.T(iNearby)),']')},...
                    'FontWeight','bold','Units','normalized'...
                    );
                delete(h);
                hold on;
                polarcont(df.Z(iNearby).freqBin,metToMathAngle(df.Z(iNearby).dirBin),df.Z(iNearby).spec);
                cb = colorbar;
                xlabel('Radius = Frequency (Hz)');
                set(get(cb,'ylabel'),'String','Density (m^2/Hz)');
                hold off;
            end
        end
        
        function M = plotField(df,plotType,fieldName,cropExtent)
            if(nargin<3)
                error('Must specify plotType and fieldName (e.g. "scatter" for a datafield with spectra objects you can specify ''Hs''');
            end
            if(nargin<4)
                cropExtent = df.boundingBox;
            end
            
            if(cropExtent.tb~=cropExtent.te)
                uniqueT = unique(df.T);
                tbetween = sort(uniqueT(uniqueT >= cropExtent.tb & uniqueT <= cropExtent.te));
                for i=1:length(tbetween)
                    if(strcmp(plotType,'quiver'))
                        df.makeVectorPlot(cropExtent,tbetween(i));
                    else
                        df.makeFieldPlot(plotType,fieldName,cropExtent,tbetween(i));
                    end
                    %axis equal;
                    M(i) = getframe(gcf);
                end
            else
                if(strcmp(plotType,'quiver'))
                    df.makeVectorPlot(cropExtent,cropExtent.tb);
                else
                    df.makeFieldPlot(plotType,fieldName,cropExtent,cropExtent.tb);
                end
                M = getframe(gcf);
            end
        end
        
        function makeFieldPlot(df,plotType,fieldName,cropExtent,t)
            clf;
            cropExtent.tb = t;
            cropExtent.te = t;
            inds = df.isInCropExtent(cropExtent);
            fieldInd = find(strcmp(df.scalarFields,fieldName));
            
            if(strcmp(plotType,'scatter'))
                Z = df.interpFuns{fieldInd}(df.X(inds),df.Y(inds),df.T(inds));
            else
                sortedXY = sortrows([df.X(inds),df.Y(inds)],[1,2]);
                [X,Y,T] = meshgrid(sortedXY(:,1),sortedXY(:,2),t);
                Z = df.interpFuns{fieldInd}(X,Y,T);
                Z(isnan(Z)) = -1;
            end
            
            if(strcmp(plotType,'surf'))
                surf(X,Y,Z);
                shading('interp');
            elseif(strcmp(plotType,'contour'))
                contour(X,Y,Z);
            elseif(strcmp(plotType,'scatter'))
                scatter(df.X(inds),df.Y(inds),Z.^2,Z,'filled');
            end
            colorbar();
            view(2);
            set(gcf(),'Color','White');
            set(gca(),'Position',get(gca(),'Position')+[0,0,0,-.1]);
            
            title({[fieldName,' -- ',regexprep(char(df.Z(inds(1)).getSourceName),'\_','\\_')],...
                strcat('[',dateLabel(df.T(inds(1))),']')},...
                'FontWeight','bold','Units','normalized'...
                );
            xlabel('Longitude (\circE)');
            ylabel('Latitude (\circN)');
        end
        
        
        function makeVectorPlot(df,cropExtent,t)
            clf;
            cropExtent.tb = t;
            cropExtent.te = t;
            inds = df.isInCropExtent(cropExtent);
            speedInd = find(strcmp(df.scalarFields,'speed'));
            dirInd = find(strcmp(df.scalarFields,'dir'));
           
            % The following down samples the data to a regular grid with
            % nGrid segments (nGrid+1 points)
            nGrid = 30;
            xRange = max(df.X(inds))-min(df.X(inds));
            xSparse = min(df.X(inds)) + [0:nGrid]*xRange/nGrid;
            yRange = max(df.Y(inds))-min(df.Y(inds));
            ySparse = min(df.Y(inds)) + [0:nGrid]*yRange/nGrid;
            sortedXY = sortrows([xSparse',ySparse'],[1,2]);

                        
          %  sortedXY = sortrows([df.X(inds),df.Y(inds)],[1,2]);
            [X,Y,T] = meshgrid(sortedXY(:,1),sortedXY(:,2),t);
            Zspeed = df.interpFuns{speedInd}(X,Y,T);
            Zdir = df.interpFuns{dirInd}(X,Y,T);
            %X = X(:,size(X,2):-1:1);
            
            
            U = Zspeed.*cos(Zdir.*pi./180);
            V = Zspeed.*sin(Zdir.*pi./180);
            U(isnan(V)) = 0;
            V(isnan(V)) = 0;
          
            centerLon = (cropExtent.ll(1)+ cropExtent.ur(1))/2;
            
            m_proj('oblique mercator','longitudes',[centerLon centerLon], ...
'latitudes',[cropExtent.ur(2) cropExtent.ll(2)],'aspect',1);
            m_coast('patch',[.7 .7 .7],'edgecolor','none');
            m_grid;
            hold on;
            m_quiver(X,Y,U,V);
            m_contour(X,Y,Zspeed);
            hold off;
            view(2);
            set(gcf(),'Color','White');
            set(gca(),'Position',get(gca(),'Position')+[0,0,0,-.1]);
            
            title({['Velocity -- ',regexprep(char(df.Z(inds(1)).getSourceName),'\_','\\_')],...
                strcat('[',dateLabel(df.T(inds(1))),']')},...
                'FontWeight','bold','Units','normalized'...
                );
            xlabel('Longitude (\circE)');
            ylabel('Latitude (\circN)');
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
