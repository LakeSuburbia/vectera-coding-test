import pytest

from meetings.models import Meeting, Note, Summary


@pytest.mark.django_db
def test_meetings_ordering(meeting):
    # The meetings should be ordered by started_at descending by default
    old_meeting = Meeting.objects.create(title="Old meeting", started_at="1900-01-01T10:00:00Z")
    assert list(Meeting.objects.all()) == [meeting, old_meeting]


@pytest.mark.django_db
def test_notes_ordering(meeting):
    # The notes should be ordered by created_at ascending by default
    first = Note.objects.create(meeting=meeting, author="Alice", text="First")
    second = Note.objects.create(meeting=meeting, author="Bob", text="Second")

    assert list(Note.objects.filter(meeting=meeting)) == [first, second]


@pytest.mark.django_db
def test_summary_initialize_creates_pending_summary(meeting):
    summary = Summary.objects.initialize(meeting_id=meeting.id)

    assert summary.status == Summary.PENDING
    assert summary.meeting_id == meeting.id
    assert summary.content == ""


@pytest.mark.django_db
def test_summary_initialize_is_idempotent_per_meeting(meeting):
    first = Summary.objects.initialize(meeting_id=meeting.id)
    second = Summary.objects.initialize(meeting_id=meeting.id)

    assert first.id == second.id
    assert Summary.objects.filter(meeting_id=meeting.id).count() == 1


@pytest.mark.django_db
def test_summary_write_sets_ready_status_with_content(meeting):
    summary = Summary.objects.initialize(meeting_id=meeting.id)

    summary.write("Discussed the roadmap.")
    summary.refresh_from_db()

    assert summary.status == Summary.READY
    assert summary.content == "Discussed the roadmap."


@pytest.mark.django_db
def test_summary_write_marks_failed_when_content_is_empty(meeting):
    summary = Summary.objects.initialize(meeting_id=meeting.id)

    summary.write("")
    summary.refresh_from_db()

    assert summary.status == Summary.FAILED


@pytest.mark.django_db
def test_summary_write_raises_once_ready(meeting):
    summary = Summary.objects.initialize(meeting_id=meeting.id)
    summary.write("Final content")

    with pytest.raises(ValueError):
        summary.write("Trying to overwrite")


@pytest.mark.django_db
def test_summary_fail_sets_failed_status(meeting):
    summary = Summary.objects.initialize(meeting_id=meeting.id)

    summary.fail(Exception("boom"))
    summary.refresh_from_db()

    assert summary.status == Summary.FAILED
