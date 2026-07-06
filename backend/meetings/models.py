import logging

from django.db import models

log = logging.getLogger(__name__)


class Meeting(models.Model):
    title = models.CharField(max_length=200)
    started_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]


class NoteManager(models.Manager):
    def create(self, meeting_id, author, text):
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
    def initialize(self, meeting_id):
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

    def write(self, content):
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

    def fail(self, exception=None):
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
