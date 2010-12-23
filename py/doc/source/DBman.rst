The ``DBman`` Module
====================

.. automodule:: wavecon.DBman

Class Functions
---------------

.. autofunction:: wavecon.DBman.recordToDict
.. autofunction:: wavecon.DBman.recoverWKT
   
Database Access Functions
-------------------------

.. autofunction:: wavecon.DBman.accessTable
.. autofunction:: wavecon.DBman.startSession
.. autofunction:: wavecon.DBman.bulk_import

Example
-------

The following is an example useage of DBman to insert a ``Wind`` object into
the database table ``tblWind``:

.. literalinclude:: ../../tests/dbtest.py
   :lines: 12-
