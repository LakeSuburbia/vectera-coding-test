import pytest
from rest_framework import status

from meetings.models import Note, Summary
from meetings.services.ai import client as ai_client


@pytest.mark.django_db
def test_health_check(api_client):
    response = api_client.get("/api/health/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"status": "ok"}


@pytest.mark.django_db
def test_create_and_list_meetings(api_client):
    create_response = api_client.post(
        "/api/meetings/",
        {"title": "Sprint planning", "started_at": "2026-07-01T10:00:00Z"},
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    assert create_response.data["note_count"] == 0
    assert create_response.data["latest_summary"] is None

    list_response = api_client.get("/api/meetings/")

    assert list_response.status_code == status.HTTP_200_OK
    assert list_response.data["count"] == 1
    assert list_response.data["results"][0]["title"] == "Sprint planning"


@pytest.mark.django_db
def test_add_and_list_notes_happy_path(api_client, meeting):
    add_response = api_client.post(
        f"/api/meetings/{meeting.id}/notes/",
        {"author": "Alice", "text": "Discussed the roadmap."},
    )

    assert add_response.status_code == status.HTTP_201_CREATED
    assert add_response.data["author"] == "Alice"

    list_response = api_client.get(f"/api/meetings/{meeting.id}/notes/")

    assert list_response.status_code == status.HTTP_200_OK
    assert list_response.data["count"] == 1
    assert list_response.data["results"][0]["text"] == "Discussed the roadmap."


@pytest.mark.django_db
def test_summarize_happy_path(api_client, meeting, monkeypatch):
    Note.objects.create(meeting=meeting, author="Alice", text="Discussed the roadmap.")

    async def fake_summarize(text):
        return "Summary of the roadmap discussion."

    monkeypatch.setattr(ai_client, "summarize", fake_summarize)

    summarize_response = api_client.post(f"/api/meetings/{meeting.id}/summarize/")
    assert summarize_response.status_code == status.HTTP_200_OK

    summary_response = api_client.get(f"/api/meetings/{meeting.id}/summary/")

    assert summary_response.status_code == status.HTTP_200_OK
    assert summary_response.data["detail"]["status"] == Summary.READY
    assert (
        summary_response.data["detail"]["content"]
        == "Summary of the roadmap discussion."
    )


@pytest.mark.django_db
def test_summarize_failure_marks_summary_failed(api_client, meeting, monkeypatch):
    async def failing_summarize(text):
        raise RuntimeError("Anthropic API unavailable")

    monkeypatch.setattr(ai_client, "summarize", failing_summarize)

    summarize_response = api_client.post(f"/api/meetings/{meeting.id}/summarize/")
    assert summarize_response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    summary_response = api_client.get(f"/api/meetings/{meeting.id}/summary/")

    assert summary_response.status_code == status.HTTP_200_OK
    assert summary_response.data["detail"]["status"] == Summary.FAILED


@pytest.mark.django_db
def test_create_meeting_missing_fields_returns_400(api_client):
    response = api_client.post("/api/meetings/", {"title": ""})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "title" in response.data
    assert "started_at" in response.data


@pytest.mark.django_db
def test_add_note_missing_fields_returns_400(api_client, meeting):
    response = api_client.post(f"/api/meetings/{meeting.id}/notes/", {"author": ""})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "author" in response.data
    assert "text" in response.data


@pytest.mark.django_db
def test_notes_for_nonexistent_meeting_returns_404(api_client):
    response = api_client.post(
        "/api/meetings/999999/notes/", {"author": "Alice", "text": "Hi"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_summary_for_meeting_without_summary_returns_404(api_client, meeting):
    response = api_client.get(f"/api/meetings/{meeting.id}/summary/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
