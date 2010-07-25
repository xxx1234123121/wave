The ``DBman`` Module
====================

.. automodule:: wavecon.DBman

.. todo::
   Describe session usage- how it is best to create one global session
   per module to avoid "Maximum Connections Exceeded" errors and the
   overhead involved with opening/closing sessions in each function
   call (can double execution time).

Class Descriptions
------------------

.. todo::
   Describe class attributes and synonyms.

   
Database Access Functions
-------------------------

.. autofunction:: wavecon.DBman.accessTable
.. autofunction:: wavecon.DBman.startSession

Example
-------

The following is an example useage of DBman to insert a ``Wind`` object into
the database table ``tblWind``::

  from wavecon.config import DBconfig
  from wavecon import DBman

  from datetime import datetime

  Wind = DBman.accessTable( DBconfig, 'tblwind', 'tblwind' )
  session = DBman.startSession( DBconfig )

  windTest = Wind( '1', 'POINT(40.86 -124.08)', datetime.now(), 12.0, 120.0 )
  print windTest

  session.add(windTest)
  session.commit()

  for record in session.query(Wind):
    print session.scalar(record.winlocation.wkt)

  session.close()
