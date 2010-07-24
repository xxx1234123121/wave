The ``config`` Module
=====================

.. automodule:: wavecon.config

Ready-to-use Configuration Info
-------------------------------

These objects contain pre-defined constants or the results of
reading in certain files in the top-level ``config`` directory.
They are ready to use through a simple ``import`` statement.::

  from wavecon.config import DBconfig
  
  # Now you can connect to the database!
  import wavecon.DBman
  session = DBman.startSession( DBconfig )

.. autodata:: wavecon.config.CONFIG_DIR
.. autodata:: wavecon.config.DBconfig
