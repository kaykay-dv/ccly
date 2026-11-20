from django.conf import settings


def test_health_view_is_public():
    if not settings.configured:
        import pytest

        pytest.skip("Django settings are not configured.")
    from rest_framework.permissions import AllowAny

    from __APP_NAME__.views import HealthView

    assert AllowAny in HealthView.permission_classes
