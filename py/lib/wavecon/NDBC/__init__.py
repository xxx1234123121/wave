"""
Overview
--------

This module interfaces with the National Data Buoy Center (NDBC) archives and
extracts wave data and wind data for NDBC 3 meter buoys and SCRIPPS waverider
buoys.

The primary interface is ``py/bin/buoyboy.py`` which is a python command line
script.  BuoyBoy must be able to find the ``py/lib/wavecon`` module.  A
description of the command line arguments can be obtained by running ``python
buoyboy.py --help`` in the command prompt.  Example usages of BuoyBoy can be
found in the file ``py/tests/buoyboy``.

The NDBC module can format downloaded data into the following formats:

- JavaScript Object Notation (JSON) through the standard python json module.
- Matlab ``.mat`` files using the ``savemat`` function contained in the
  ``scipy.io`` module.

.. note::
  
   Matlab output has been found to require the following:

   - Python version 2.7 or greater.
   - NumPy version 1.5 or greater.
   - SciPy version 0.8 or greater.

   Previous versions have been found to be incapable of transcribing Python
   objects to Matlab Structs and Cell Arrays.

- SQL records to commit to a PostGIS database through the SqlAlchemy and
  GeoAlchemy modules (currently disabled due to code reorginizaiton).

Downloaded Data
---------------

The NDBC module downloads two types of data- wind records and wave records.

A wind record is a structure that contains the following::

  {
    'buoyNumber': # The NDBC buoy number.
    'datetime':   # An ISO 8601 datestring.
    'winDirection': # The wind direction in nautical degrees.
    'winSpeed': # The windspeed in knots.
  }

A wave record is a structure that **MAY** contain the following::

  {
    'buoyNumber': # The NDBC buoy number (will be present).
    'datetime':   # An ISO 8601 datestring (will be present).
    'wavPeakDir': # The peak direction (may be missing).
    'wavPeakPeriod': # The peak period (may be missing).
    'wavHeight': # The significant wave height (may be missing).
    'density': # The frequency spectra (may be missing).
    'densityBins': # The cut values used to partition the frequency spectra.
                   # (may be missing if density is missing).
    'directionAlpha1': # The Alpha1 direction spectra (may be missing).
    'directionAlpha1Bins': # The cut values used to partition the Alpha1 spectra.
                           # (may be missing if directionAlpha1 is missing).
    'directionAlpha2': # The Alpha2 direction spectra (may be missing).
    'directionAlpha2Bins': # The cut values used to partition the Alpha2 spectra.
                           # (may be missing if directionAlpha2 is missing).
    'directionR1': # The R1 direction spectra (may be missing).
    'directionR1Bins': # The cut values used to partition the R1 spectra.
                       # (may be missing if directionR1 is missing).
    'directionR2': # The R2 direction spectra (may be missing).
    'directionR2Bins': # The cut values used to partition the R2 spectra.
                       # (may be missing if directionR2 is missing).
  }
"""
from .downloader import fetchBuoyRecords
