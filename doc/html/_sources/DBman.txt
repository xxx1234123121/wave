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
the database table ``tblWind``:

.. literalinclude:: ../../tests/dbtest.py
   :lines: 12-
