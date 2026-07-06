import pytest
from rest_framework.test import APIClient

from meetings.models import Meeting


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def meeting() -> Meeting:
    return Meeting.objects.create(
        title="Sprint planning", started_at="2026-07-01T10:00:00Z"
    )
