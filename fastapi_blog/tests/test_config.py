
from app.config import settings


def test_hosts_list():
    assert settings.hosts_list == [
        host.strip()
        for host in settings.allowed_hosts.split(",")
    ]


def test_origins_list():
    assert settings.origins_list == [
        origin.strip()
        for origin in settings.allowed_origins.split(",")
    ]


def test_is_production():
    assert isinstance(settings.is_production, bool)
