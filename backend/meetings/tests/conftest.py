import pytest
from rest_framework.test import APIClient

from meetings.models import Meeting, Summary
from meetings.services.ai import client as ai_client


class MockAIClient:
    result: str | BaseException = "This is a mocked summary."

    async def summarize(self, notes: str) -> str:
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result


@pytest.fixture
def mock_ai_client(monkeypatch: pytest.MonkeyPatch) -> MockAIClient:
    mock = MockAIClient()
    monkeypatch.setattr(ai_client, "summarize", mock.summarize)
    return mock


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def meeting() -> Meeting:
    return Meeting.objects.create(
        title="Sprint planning", started_at="2026-07-01T10:00:00Z"
    )
