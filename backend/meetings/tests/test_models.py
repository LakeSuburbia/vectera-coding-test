import pytest

from meetings.models import Meeting, Note, Summary


@pytest.fixture
def running_summary(meeting: Meeting, monkeypatch: pytest.MonkeyPatch) -> Summary:
    """A summary that has been started (status=RUNNING) but whose job body
    never actually runs, so tests can drive write()/fail() directly."""
    monkeypatch.setattr(Summary, "_spawn", lambda self, target, *args: None)
    summary = Summary.objects.initialize(meeting_id=meeting.id)
    summary.start()
    return summary


@pytest.mark.django_db
def test_meetings_ordering(meeting: Meeting) -> None:
    # The meetings should be ordered by started_at descending by default
    old_meeting = Meeting.objects.create(
        title="Old meeting", started_at="1900-01-01T10:00:00Z"
    )
    assert list(Meeting.objects.all()) == [meeting, old_meeting]


@pytest.mark.django_db
def test_notes_ordering(meeting: Meeting) -> None:
    # The notes should be ordered by created_at ascending by default
    first = Note.objects.create(meeting_id=meeting.id, author="Alice", text="First")
    second = Note.objects.create(meeting_id=meeting.id, author="Bob", text="Second")

    assert list(Note.objects.filter(meeting_id=meeting.id)) == [first, second]


@pytest.mark.django_db
def test_summary_initialize_creates_pending_summary(meeting: Meeting) -> None:
    summary = Summary.objects.initialize(meeting_id=meeting.id)

    assert summary.status == Summary.PENDING
    assert summary.meeting_id == meeting.id
    assert summary.content == ""


@pytest.mark.django_db
def test_summary_initialize_is_idempotent_per_meeting(meeting):
    first = Summary.objects.initialize(meeting_id=meeting.id)
    second = Summary.objects.initialize(meeting_id=meeting.id)

    assert first.id == second.id
    assert Summary.objects.filter(meeting=meeting).count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content", ["Discussed the roadmap.", "A" * 50000], ids=["short", "long"]
)
def test_summary_write_sets_ready_status_with_content(
    running_summary: Summary, content: str
) -> None:
    running_summary.write(content)
    running_summary.refresh_from_db()

    assert running_summary.status == Summary.READY
    assert running_summary.content == content


@pytest.mark.django_db
@pytest.mark.parametrize("content", ["", None])
def test_summary_write_marks_failed_when_content_is_empty(
    running_summary: Summary, content: str
) -> None:
    running_summary.write(content)
    running_summary.refresh_from_db()

    assert running_summary.status == Summary.FAILED


@pytest.mark.django_db
def test_summary_write_raises_when_not_running(meeting: Meeting) -> None:
    summary = Summary.objects.initialize(meeting_id=meeting.id)

    with pytest.raises(ValueError):
        summary.write("Too early, job was never started.")


@pytest.mark.django_db
def test_summary_write_raises_once_ready(running_summary: Summary) -> None:
    running_summary.write("Final content")

    with pytest.raises(ValueError):
        running_summary.write("Trying to overwrite")


@pytest.mark.django_db
@pytest.mark.parametrize("exception", [None, Exception("boom")])
def test_summary_fail_sets_failed_status(running_summary: Summary, exception) -> None:
    running_summary.fail(exception)
    running_summary.refresh_from_db()

    assert running_summary.status == Summary.FAILED


@pytest.mark.django_db
def test_summary_fail_raises_when_not_running(meeting: Meeting) -> None:
    summary = Summary.objects.initialize(meeting_id=meeting.id)

    with pytest.raises(ValueError):
        summary.fail()


@pytest.mark.django_db
def test_summary_start_rejects_second_call_while_job_is_running(
    meeting: Meeting, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Summary, "_spawn", lambda self, target, *args: None)
    summary = Summary.objects.initialize(meeting_id=meeting.id)

    summary.start()

    with pytest.raises(Summary.AlreadyRunning):
        summary.start()


@pytest.mark.django_db
def test_summary_start_allowed_again_once_previous_job_finished(
    meeting: Meeting, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Summary, "_spawn", lambda self, target, *args: None)
    summary = Summary.objects.initialize(meeting_id=meeting.id)
    summary.start()
    summary.write("Done.")

    summary = Summary.objects.initialize(meeting_id=meeting.id)
    summary.start()  # should not raise: previous job reached READY, so PENDING again
