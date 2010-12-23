function [ lab ] = locationLabel( lat, lon, time )
%latLonLabel Formats a latitude and longitude into a consice label
    lab = [num2str(lat),'\circE, ',num2str(lon),'\circN --- ',dateLabel(time)];
end

