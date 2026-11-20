"""Settings this app adds to the ccly Django project.

Uppercase names defined here become Django settings. A name that already
exists is replaced. ``INSTALLED_APPS`` is appended to the project's list.
Do not import Django settings from this module.

A value that differs per deployment is read from the site ``.env`` file.
``env`` advertises that variable to ccly. ``required=True`` makes startup
fail until the variable is set.
"""

# Static path of the logo beside the project name in the admin navbar.
# Put a replacement file in this app's static directory and change the path.
CCLY_LOGO = "img/alaska.png"

# from ccly.env import env
# CCLY_API_KEY = env("CCLY_API_KEY", required=True)
# EXTERNAL_API_URL = "https://api.example.com"
# INSTALLED_APPS = ["third.party.app"]
