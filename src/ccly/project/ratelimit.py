"""Site-wide rate limit driven by the CCLY_RATELIMIT_* variables."""

from django.conf import settings
from django_ratelimit.core import is_ratelimited
from django_ratelimit.exceptions import Ratelimited


class RatelimitMiddleware:
    """Count requests for the whole site and reject those past the rate.

    Signed-in users are counted separately. Anonymous requests are counted
    by IP. Static files are left alone so the admin can load its assets.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not _is_static(request) and _is_limited(request):
            raise Ratelimited()
        return self.get_response(request)


def _is_limited(request) -> bool:
    return is_ratelimited(
        request,
        group="ccly",
        key=settings.CCLY_RATELIMIT_KEY,
        rate=settings.CCLY_RATELIMIT_RATE,
        increment=True,
    )


def _is_static(request) -> bool:
    static_url = getattr(settings, "STATIC_URL", "") or ""
    if static_url.startswith(("http://", "https://")):
        return False
    prefix = "/" + static_url.lstrip("/")
    return request.path.startswith(prefix)
