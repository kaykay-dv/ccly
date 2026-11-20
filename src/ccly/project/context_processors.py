def admin_brand(request):
    """Expose the admin title and logo to pages that are not rendered by AdminSite."""
    from django.conf import settings
    from django.contrib import admin

    return {
        "site_header": admin.site.site_header,
        "site_title": admin.site.site_title,
        "CCLY_LOGO": getattr(settings, "CCLY_LOGO", ""),
    }
