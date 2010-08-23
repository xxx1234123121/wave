WaveConnect GIS Resources
=========================

This project contains GIS resources assembled for the PG&E WaveConnect
resource assessment survey. The files are formatted in such a way that they
should be accessible to a wide range of tools.  For raster imagry, the GeoTIFF
format is preferred; for vector data the KML format is used.  Raw data has been
obtained from various sources, which are described in this documentation, and
manipulated using the GDAL library to produce GeoTIFF and KML files.  All
datasets have been reprojected into the ``EPSG:4326`` spatial reference system.

The freely available QGIS program has been used to organize and display the
datasets.  The main QGIS file is ``WaveConnect.qgs``. QGIS
and GDAL are described later on in this document.

Included Datasets
-----------------

This project contains the following files:

::

    GIS
    |- README.html
    |    A link to this documentation.
    |- WaveConnect.qgs  
    |    Main QGIS Project file.
    |- Bathymetry
    |  |- bathy
    |  |    Contains raster datasets from bathymetry surveys.
    |  |- bound
    |       Vector outlines of bathymetry survey areas.
    |- NDBCbuoys
    |    Vector dataset showing the location of NDBC buoys.
    |- StudyArea
    |    Vector outline of the WaveConnect project area.
    |- HFradarCoverage
    |    Location and coverage of the High-Frequency radar installation in
    |    Trinidad.
    |- NOAAcharts
    |    Raster imagry of NOAA nautical charts.
    |- SWANgrids
    |    Coverage area of a SWAN modle that was used by the National Weather
    |    Service.
    |- doc
         Contains the Sphinx source code for this documentation.

Documentation specific to each dataset can is contained in the following pages
and explains where the data was obtained from and what post-processing steps
were used:

.. toctree::
   :maxdepth: 1

   SurveyBathy
   SurveyBounds
   NDBCbuoys
   NOAAcharts

Tools
-----

QGIS
++++

Quantum GIS (QGIS) is an open source Geospatial Information System (GIS) that is
used to assemble and manage the datasets described by this document. QGIS was
chosen because it is cost effective and meets developer requirements for support
across a diverse range of platforms. The following webpages contain info
relevant to obtaining and using QGIS:

-  *The QGIS homepage:*
   `http://www.qgis.org/ <http://www.qgis.org/>`_
-  *The QGIS downloads page:*
   `http://www.qgis.org/en/download/current-software.html <http://www.qgis.org/en/download/current-software.html>`_
-  *Mac OS X binaries:*
   `http://www.kyngchaos.com/software:qgis <http://www.kyngchaos.com/software:qgis>`_
   (The "standalone" Mac binaries are recommended as they require the
   installation of no additional components and are self-contained and
   easy to uninstall)

.. note::
   QGIS version 1.5 or higher should be used to view the 
   ``WaveConnect.qgs`` file.
 
GDAL
++++

The Geospatial Data Abstraction Library (GDAL) is the standard open
source tool kit for manipulating and transcoding geospatial data.
The following tools provided by the GDAL library were used
extensively in the production of this data:


-  ``gdal_translate``: Used to translate raster data from
   proprietary formats, such as ArcGIS coverages, or esoteric formats
   such as NOAA BSB files to commonly used raster formats such as
   GeoTIFF.
-  ``gdalwarp``: Used to reproject raster data from coordinate
   systems such as Universal Transverse Mercator (UTM) to the common
   EPSG:4326 Lat/Lon projection used throughout this project.
   ``gdalwarp`` was also used to merge or "mosaic" several raster
   datasets into one unified dataset.
-  ``ogr2ogr``: Used to reproject and reformat vector data.

Information and source code for GDAL can be obtained from the
following webpages:


-  *The GDAL Homepage:*
   `http://www.gdal.org/ <http://www.gdal.org/>`_
-  *GDAL Binaries:*
   `http://trac.osgeo.org/gdal/wiki/DownloadingGdalBinaries <http://trac.osgeo.org/gdal/wiki/DownloadingGdalBinaries>`_

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

