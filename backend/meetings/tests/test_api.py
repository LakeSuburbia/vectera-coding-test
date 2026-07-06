import asyncio
import threading

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from meetings import views
from meetings.models import Meeting, Note, Summary
from meetings.services.ai import client as ai_client


def _run_spawn_inline(target, *args) -> None:
    """Test stand-in for views._spawn: runs the job synchronously on the calling thread."""
    target(*args)


@pytest.mark.django_db
def test_health_check(api_client: APIClient) -> None:
    response = api_client.get("/api/health/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"status": "ok"}


@pytest.mark.django_db
def test_create_and_list_meetings(api_client: APIClient) -> None:
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
def test_list_meetings_query_count_is_independent_of_meeting_count(
    api_client: APIClient, django_assert_num_queries
) -> None:
    for i in range(3):
        meeting = Meeting.objects.create(
            title=f"Meeting {i}", started_at="2026-07-01T10:00:00Z"
        )
        Summary.objects.initialize(meeting_id=meeting.id)

    # 1 query for the pagination count, 1 for the page of meetings (summary
    # joined via select_related). Without select_related this would grow by
    # one extra query per meeting on the page.
    with django_assert_num_queries(2):
        response = api_client.get("/api/meetings/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3


@pytest.mark.django_db
def test_add_and_list_notes_happy_path(api_client: APIClient, meeting: Meeting) -> None:
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
def test_summarize_happy_path(api_client: APIClient, meeting: Meeting, monkeypatch: pytest.MonkeyPatch) -> None:
    Note.objects.create(meeting_id=meeting.id, author="Alice", text="Discussed the roadmap.")

    async def fake_summarize(text: str) -> str:
        return "Summary of the roadmap discussion."

    monkeypatch.setattr(ai_client, "summarize", fake_summarize)
    monkeypatch.setattr(views, "_spawn", _run_spawn_inline)

    summarize_response = api_client.post(f"/api/meetings/{meeting.id}/summarize/")
    assert summarize_response.status_code == status.HTTP_202_ACCEPTED

    summary_response = api_client.get(f"/api/meetings/{meeting.id}/summary/")

    assert summary_response.status_code == status.HTTP_200_OK
    assert summary_response.data["detail"]["status"] == Summary.READY
    assert (
        summary_response.data["detail"]["content"]
        == "Summary of the roadmap discussion."
    )


@pytest.mark.django_db
def test_summarize_failure_marks_summary_failed(api_client: APIClient, meeting: Meeting, monkeypatch: pytest.MonkeyPatch) -> None:
    async def failing_summarize(text: str) -> str:
        raise RuntimeError("Anthropic API unavailable")

    monkeypatch.setattr(ai_client, "summarize", failing_summarize)
    monkeypatch.setattr(views, "_spawn", _run_spawn_inline)

    summarize_response = api_client.post(f"/api/meetings/{meeting.id}/summarize/")
    assert summarize_response.status_code == status.HTTP_202_ACCEPTED

    summary_response = api_client.get(f"/api/meetings/{meeting.id}/summary/")

    assert summary_response.status_code == status.HTTP_200_OK
    assert summary_response.data["detail"]["status"] == Summary.FAILED


@pytest.mark.django_db(transaction=True)
def test_summarize_runs_in_background_and_reports_pending_until_complete(
    api_client: APIClient, meeting: Meeting, monkeypatch: pytest.MonkeyPatch
) -> None:
    started = threading.Event()
    release = threading.Event()
    threads: list[threading.Thread] = []

    def tracking_spawn(target, *args) -> None:
        thread = threading.Thread(target=target, args=args, daemon=True)
        threads.append(thread)
        thread.start()

    async def slow_summarize(text: str) -> str:
        started.set()
        await asyncio.get_event_loop().run_in_executor(None, release.wait)
        return "Async summary."

    monkeypatch.setattr(views, "_spawn", tracking_spawn)
    monkeypatch.setattr(ai_client, "summarize", slow_summarize)

    summarize_response = api_client.post(f"/api/meetings/{meeting.id}/summarize/")
    assert summarize_response.status_code == status.HTTP_202_ACCEPTED

    assert started.wait(timeout=2), "background job never started"
    pending_response = api_client.get(f"/api/meetings/{meeting.id}/summary/")
    assert pending_response.data["detail"]["status"] == Summary.PENDING

    release.set()
    threads[0].join(timeout=2)

    ready_response = api_client.get(f"/api/meetings/{meeting.id}/summary/")
    assert ready_response.data["detail"]["status"] == Summary.READY
    assert ready_response.data["detail"]["content"] == "Async summary."


@pytest.mark.django_db
def test_create_meeting_missing_fields_returns_400(api_client: APIClient) -> None:
    response = api_client.post("/api/meetings/", {"title": ""})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "title" in response.data
    assert "started_at" in response.data


@pytest.mark.django_db
def test_add_note_missing_fields_returns_400(api_client: APIClient, meeting: Meeting) -> None:
    response = api_client.post(f"/api/meetings/{meeting.id}/notes/", {"author": ""})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "author" in response.data
    assert "text" in response.data


@pytest.mark.django_db
def test_notes_for_nonexistent_meeting_returns_404(api_client: APIClient) -> None:
    response = api_client.post(
        "/api/meetings/999999/notes/", {"author": "Alice", "text": "Hi"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_summary_for_meeting_without_summary_returns_404(api_client: APIClient, meeting: Meeting) -> None:
    response = api_client.get(f"/api/meetings/{meeting.id}/summary/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
