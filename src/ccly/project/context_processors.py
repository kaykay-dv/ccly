def admin_brand(request):
    """Expose the admin title to pages that are not rendered by AdminSite."""
    from django.contrib import admin

    return {
        "site_header": admin.site.site_header,
        "site_title": admin.site.site_title,
    }
