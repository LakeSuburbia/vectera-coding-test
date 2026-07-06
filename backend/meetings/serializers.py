from rest_framework import serializers
from .models import Meeting, Note, Summary

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "author", "text", "created_at"]

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ["id", "content", "status", "created_at", "updated_at"]

class PostSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = []

class MeetingSerializer(serializers.ModelSerializer):
    note_count = serializers.IntegerField(read_only=True)
    latest_summary = SummarySerializer(source="summary", read_only=True)

    class Meta:
        model = Meeting
        fields = ["id", "title", "started_at", "created_at", "note_count", "latest_summary"]
