"""Settings this app adds to the ccly Django project.

Uppercase names defined here become Django settings. They ship with the
package, so they are the same for every deployment. A name that already
exists is replaced. ``INSTALLED_APPS`` is appended to the project's list.
Do not import Django settings from this module.
"""

# Static path of the logo beside the project name in the admin navbar.
# Put a replacement file in this app's static directory and change the path.
CCLY_LOGO = "img/alaska.png"

# EXTERNAL_API_URL = "https://api.example.com"
# INSTALLED_APPS = ["third.party.app"]
