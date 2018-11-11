"""
Global fixtures
"""
# pylint: disable=redefined-outer-name
# False-positives, pretty weird but looks like some sys.path
# mishandlling pylint is known to at times
import py.path  # pylint: disable=import-error,no-name-in-module
import pytest
import pytest_django
from django.conf import settings
from django.test import RequestFactory
from rest_framework.test import APIClient

from pizzeria_dangelo.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(
        settings: pytest_django.fixtures.SettingsWrapper,
        tmpdir: py.path.local,  # pylint: disable=no-member
) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> settings.AUTH_USER_MODEL:
    return UserFactory()


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def client() -> APIClient:
    return APIClient()
