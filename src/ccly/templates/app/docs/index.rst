__APP_NAME__
================================================================================

A Django app packaged for PyPI and loaded by ccly.

``GET /__APP_NAME__/health/`` returns the JSON string ``"OK"``.

Run it
------

From the site directory, where the ``.env`` file lives:

.. code-block:: bash

   ccly init __APP_NAME__
   ccly migrate
   ccly runserver

Settings that belong to this package live in ``ccly_settings.py``.
Values that differ per deployment are read from the site ``.env`` file.
