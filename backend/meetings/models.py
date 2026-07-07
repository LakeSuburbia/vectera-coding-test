from __future__ import annotations

import logging
import threading
from typing import Any, Callable

import pglock
from asgiref.sync import async_to_sync
from django.db import connection, models

from .services.ai import client as ai_client

log = logging.getLogger(__name__)


def _summary_lock(meeting_id: int) -> pglock.advisory:
    return pglock.advisory(f"meetings.summary:{meeting_id}")


class Meeting(models.Model):
    title = models.CharField(max_length=200)
    started_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]


class NoteManager(models.Manager):
    def create(self, meeting_id: int, author: str, text: str) -> "Note":
        note = super().create(meeting_id=meeting_id, author=author, text=text)
        log.info("Note added to meeting %s by %s", meeting_id, author)
        return note


class Note(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="notes")
    author = models.CharField(max_length=120)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = NoteManager()

    class Meta:
        indexes = [
            models.Index(fields=["meeting", "created_at"]),
        ]
        ordering = ["created_at"]


class SummaryManager(models.Manager):
    def initialize(self, meeting_id: int) -> "Summary":
        with _summary_lock(meeting_id):
            summary, created = self.get_or_create(
                meeting_id=meeting_id, defaults={"status": Summary.PENDING}
            )
            if not created and summary.status in (Summary.READY, Summary.FAILED):
                summary.status = Summary.PENDING
                summary.save(update_fields=["status", "updated_at"])
        return summary


class Summary(models.Model):
    PENDING = "pending"
    RUNNING = "running"
    READY = "ready"
    FAILED = "failed"
    STATUS_CHOICES = [
        (PENDING, "pending"),
        (RUNNING, "running"),
        (READY, "ready"),
        (FAILED, "failed"),
    ]

    meeting = models.OneToOneField(
        Meeting, on_delete=models.CASCADE, related_name="summary", null=True, blank=True
    )
    content = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SummaryManager()

    class Meta:
        ordering = ["-updated_at"]

    class AlreadyRunning(Exception):
        """Raised when a job is already in flight for this Summary."""

    def start(self) -> None:
        with _summary_lock(self.meeting_id):
            self.refresh_from_db()
            if self.status == Summary.RUNNING:
                raise Summary.AlreadyRunning(
                    f"A summary job is already running for meeting {self.meeting_id}."
                )
            if self.status != Summary.PENDING:
                raise ValueError(
                    "Summary is not in a pending state and cannot be started."
                )
            self.status = Summary.RUNNING
            self.save(update_fields=["status", "updated_at"])

        note_count = Note.objects.filter(meeting_id=self.meeting_id).count()
        log.info(
            "Summary requested for meeting %s (%s notes)", self.meeting_id, note_count
        )
        self._spawn(self._run_summary_job, self.meeting_id)

    def write(self, content: str) -> None:
        if self.status != Summary.RUNNING:
            raise ValueError("Summary is not running and cannot be written to.")
        previous_status, previous_content = self.status, self.content
        if content:
            self.content = content
            self.status = Summary.READY
            log.info("Summary written for meeting %s", self.meeting_id)
        else:
            self.status = Summary.FAILED
            log.warning(
                "Summary marked as failed for meeting %s due to empty content",
                self.meeting_id,
            )
        try:
            self.save()
        except Exception:
            # Keep self.status truthful if the write itself didn't persist,
            # so a subsequent fail() call still sees RUNNING and can record
            # the failure instead of raising on a stale guard.
            self.status, self.content = previous_status, previous_content
            raise

    def fail(self, exception: Exception | None = None) -> None:
        if self.status != Summary.RUNNING:
            raise ValueError(
                "Summary is not in a running state and cannot be marked as failed."
            )
        self.status = Summary.FAILED
        log.info("Summary failed for meeting %s", self.meeting_id)
        if exception:
            log.exception(
                "Exception occurred while processing summary for meeting %s: %s",
                self.meeting_id,
                exception,
            )
        self.save()

    def _spawn(self, target: Callable[..., None], *args: Any) -> None:
        def run_and_close_connection() -> None:
            try:
                target(*args)
            finally:
                connection.close()

        threading.Thread(target=run_and_close_connection, daemon=True).start()

    def _run_summary_job(self, meeting_id: int) -> None:
        try:
            summary = Summary.objects.get(meeting_id=meeting_id)
        except Summary.DoesNotExist:
            log.error(
                "Summary for meeting %s vanished before its job could run",
                meeting_id,
            )
            return
        try:
            notes = Note.objects.filter(meeting_id=meeting_id).order_by("created_at")
            concatenated_notes = "\n".join(note.text for note in notes)
            content = async_to_sync(ai_client.summarize)(concatenated_notes)
            summary.write(content)
        except Exception as e:
            try:
                summary.fail(e)
            except Exception:
                log.exception(
                    "Failed to mark summary as failed for meeting %s after a job error",
                    meeting_id,
                )
