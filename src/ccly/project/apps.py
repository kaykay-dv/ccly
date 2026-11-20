from django.apps import AppConfig


class CclyProjectConfig(AppConfig):
    name = "ccly.project"
    label = "ccly_project"
    verbose_name = "ccly"

    def ready(self) -> None:
        from django.conf import settings
        from django.contrib import admin

        admin.site.site_header = settings.CCLY_SITE_TITLE
        admin.site.site_title = settings.CCLY_SITE_TITLE
        admin.site.index_title = settings.CCLY_SITE_TITLE
