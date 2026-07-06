from __future__ import annotations

import logging
import threading
from typing import Any, Callable

from asgiref.sync import async_to_sync
from django.db import connection, models, transaction

from .services.ai import client as ai_client

log = logging.getLogger(__name__)


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
        summary, _ = self.update_or_create(
            meeting_id=meeting_id, defaults={"status": Summary.PENDING}
        )
        return summary


class Summary(models.Model):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"
    STATUS_CHOICES = [
        (PENDING, "pending"),
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

    def start(self) -> None:
        if self.status != Summary.PENDING:
            raise ValueError("Summary is not in a pending state and cannot be started.")
        note_count = Note.objects.filter(meeting_id=self.meeting).count()
        log.info(
            "Summary requested for meeting %s (%s notes)", self.meeting, note_count
        )
        self._spawn(self._run_summary_job, self.meeting_id)

    def write(self, content: str) -> None:
        if self.status == Summary.READY:
            raise ValueError("Summary has been finalized and cannot be modified.")
        if content:
            self.content = content
            self.status = Summary.READY
            log.info("Summary written for meeting %s", self.meeting)
        else:
            self.status = Summary.FAILED
            log.warning(
                "Summary marked as failed for meeting %s due to empty content",
                self.meeting,
            )
        self.save()

    def fail(self, exception: Exception | None = None) -> None:
        if not self.status == Summary.PENDING:
            raise ValueError(
                "Summary is not in a pending state and cannot be marked as failed."
            )
        self.status = Summary.FAILED
        log.info("Summary failed for meeting %s", self.meeting)
        if exception:
            log.exception(
                "Exception occurred while processing summary for meeting %s: %s",
                self.meeting,
                exception,
            )
        self.save()

    def _spawn(self, target: Callable[..., None], *args: Any) -> None:
        threading.Thread(target=target, args=args, daemon=True).start()

    def _run_summary_job(self, meeting_id: int) -> None:
        try:
            with transaction.atomic(durable=True):
                summary = Summary.objects.select_for_update().get(meeting_id=meeting_id)
                notes = Note.objects.filter(meeting_id=meeting_id).order_by(
                    "created_at"
                )
                concatenated_notes = "\n".join(note.text for note in notes)
                try:
                    content = async_to_sync(ai_client.summarize)(concatenated_notes)
                    summary.write(content)
                except Exception as e:
                    summary.fail(e)
        finally:
            connection.close()
