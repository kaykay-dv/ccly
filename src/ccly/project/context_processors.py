def admin_idle_url(path: str, app_names: list[str]) -> str:
    """Keepalive URL for an admin path, or empty when the path is not the admin."""
    for name in app_names:
        prefix = f"/{name}/m/"
        if path.startswith(prefix):
            return f"{prefix}idle/"
    return ""


def admin_brand(request):
    """Expose the admin title, logo, and idle-logout settings."""
    from django.conf import settings
    from django.contrib import admin

    return {
        "site_header": admin.site.site_header,
        "site_title": admin.site.site_title,
        "CCLY_LOGO": getattr(settings, "CCLY_LOGO", ""),
        "CCLY_ADMIN_IDLE_SECONDS": getattr(settings, "CCLY_ADMIN_IDLE_SECONDS", 0),
        "CCLY_ADMIN_IDLE_URL": admin_idle_url(
            getattr(request, "path", ""),
            getattr(settings, "CCLY_APPS", []),
        ),
        "CCLY_SESSION_COOKIE_NAME": getattr(settings, "SESSION_COOKIE_NAME", ""),
    }
