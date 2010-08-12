# NOAA Raster Nautical Charts

Georefrenced raster images of NOAA nautical charts.

**Source:** [http://www.charts.noaa.gov/InteractiveCatalog/nrnc.shtml][1]

# Raster File Processing

Transcribed from BSB format to GeoTiff and reprojected to EPSG:4326 Lat/Lon
coordinate system using:

    gdalwarp -t_srs EPSG:4326 -of Gtiff [chart#].KAP [chart#].tif

  [1]: http://www.charts.noaa.gov/InteractiveCatalog/nrnc.shtml (NOAA RNC Catalog)
