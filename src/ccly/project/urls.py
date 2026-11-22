import importlib.util

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.urls import include, path
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from ccly.extras import urlpatterns_for_apps

def _without_names(patterns: list) -> list:
    """Drop URL names so a second copy of the admin does not claim ``reverse()``."""
    for pattern in patterns:
        nested = getattr(pattern, "url_patterns", None)
        if nested is not None:
            _without_names(list(nested))
        elif getattr(pattern, "name", None):
            pattern.name = None
    return patterns


@never_cache
@require_GET
def admin_idle(request):
    """Slide the session expiry while the admin tab is in use.

    Anonymous requests are rejected so a dead session cannot be refreshed.
    """
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    return HttpResponse(status=204)


def _admin_urlpatterns(app_names: list[str]) -> list:
    """Serve the admin at ``/<app_name>/m/`` for each installed app.

    Django can register the ``admin`` URL namespace only once. The first app
    owns that namespace, so ``reverse()`` points at its admin. Further apps
    serve the same views at their own prefix.
    """
    patterns = []
    for index, app_name in enumerate(app_names):
        prefix = f"{app_name}/m/"
        named = index == 0
        patterns.extend(
            [
                path(
                    prefix + "idle/",
                    admin_idle,
                    name="admin_idle" if named else None,
                ),
                path(
                    prefix + "password_reset/",
                    auth_views.PasswordResetView.as_view(),
                    name="admin_password_reset" if named else None,
                ),
                path(
                    prefix + "password_reset/done/",
                    auth_views.PasswordResetDoneView.as_view(),
                    name="password_reset_done" if named else None,
                ),
                path(
                    prefix + "reset/<uidb64>/<token>/",
                    auth_views.PasswordResetConfirmView.as_view(),
                    name="password_reset_confirm" if named else None,
                ),
                path(
                    prefix + "reset/done/",
                    auth_views.PasswordResetCompleteView.as_view(),
                    name="password_reset_complete" if named else None,
                ),
            ]
        )
        if named:
            patterns.append(path(prefix, admin.site.urls))
        else:
            patterns.append(path(prefix, include(_without_names(admin.site.get_urls()))))
    return patterns


urlpatterns = [
    *_admin_urlpatterns(settings.CCLY_APPS),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

urlpatterns.extend(urlpatterns_for_apps(settings.CCLY_APPS))

for _app_name in settings.CCLY_APPS:
    if importlib.util.find_spec(f"{_app_name}.urls") is not None:
        urlpatterns.append(path(f"{_app_name}/", include(f"{_app_name}.urls")))
