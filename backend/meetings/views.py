import logging
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from asgiref.sync import async_to_sync
from .models import Meeting, Note, Summary
from .serializers import MeetingSerializer, NoteSerializer, SummarySerializer, PostSummarySerializer
from .services.ai import client as ai_client

log = logging.getLogger(__name__)

@api_view(["GET"])
def health(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all().annotate(note_count=Count("notes"))
    serializer_class = MeetingSerializer

    @action(detail=True, methods=["get", "post"], url_path="notes", serializer_class=NoteSerializer)
    def notes(self, request, pk=None):
        if request.method == "POST":
            return self._add_note(request, pk)
        elif request.method == "GET":
            return self._list_notes(request, pk)

    def _add_note(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = Note.objects.create(
            meeting_id=pk,
            author=serializer.validated_data["author"],
            text=serializer.validated_data["text"],
        )
        return Response(NoteSerializer(note).data, status=status.HTTP_201_CREATED)

    def _list_notes(self, request, pk=None):
        notes = Note.objects.filter(meeting_id=pk).order_by("created_at")
        page = self.paginate_queryset(notes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="summarize", serializer_class=PostSummarySerializer)
    def summarize(self, request, pk=None):
        summary = Summary.objects.initialize(meeting_id=pk)
        notes = Note.objects.filter(meeting_id=pk).order_by("created_at")
        concatenated_notes = "\n".join(note.text for note in notes)
        try:
            content = async_to_sync(ai_client.summarize)(concatenated_notes)
            summary.write(content)
            return Response({"detail": "Summary created successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            summary.fail(e)
            return Response({"detail": "Summary creation failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

    @action(detail=True, methods=["get"], url_path="summary", serializer_class=SummarySerializer)
    def get_summary(self, request, pk=None):
        try:
            summary = Summary.objects.get(meeting_id=pk)
        except Summary.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": self.get_serializer(summary).data}, status=status.HTTP_200_OK)
