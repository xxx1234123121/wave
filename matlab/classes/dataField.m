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
                    M(i) = getframe;
                end
            else
                makePointSpecPlot(df,tb,x,y,collapse);
                M = getframe;
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
            end
            %%% for now, constrain time dimension to the first time step,
            %%% later will make animation
            cropExtent.te = cropExtent.tb;
            inds = df.isInCropExtent(cropExtent);
            
            [X,Y,T] = meshgrid(df.X(inds),df.Y(inds),cropExtent.te);
            fieldInd = find(strcmp(df.scalarFields,fieldName));
            Z = df.interpFuns{fieldInd}(X,Y,T);
            Z(isnan(Z)) = 0;
            
            contour(X,Y,Z);
            colorbar();
        end
        
        function plotSurf(df,fieldName,cropExtent)
            if(nargin<2)
                error('Must specify a fieldName (e.g. for a datafield with spectra objects you can specify ''Hs''');
            end
            if(nargin<3)
                cropExtent = df.boundingBox;
            end
            %%% for now, constrain time dimension to the first time step,
            %%% later will make animation
            cropExtent.te = cropExtent.tb;
            inds = df.isInCropExtent(cropExtent);
            
            [X,Y,T] = meshgrid(df.X(inds),df.Y(inds),cropExtent.te);
            fieldInd = find(strcmp(df.scalarFields,fieldName));
            Z = df.interpFuns{fieldInd}(X,Y,T);
            Z(isnan(Z)) = 0;
            
            surf(X,Y,Z);
            shading('interp');
            colorbar();
            view(2);
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
