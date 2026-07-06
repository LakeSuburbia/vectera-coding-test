import logging

from asgiref.sync import async_to_sync
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Meeting, Note, Summary
from .serializers import (
    MeetingSerializer,
    NoteSerializer,
    PostSummarySerializer,
    SummarySerializer,
)
from .services.ai import client as ai_client

log = logging.getLogger(__name__)


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all().annotate(note_count=Count("notes"))
    serializer_class = MeetingSerializer

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="notes",
        serializer_class=NoteSerializer,
    )
    def notes(self, request: Request, pk=None) -> Response:
        meeting = self.get_object()
        if request.method == "POST":
            return self._add_note(request, meeting)
        elif request.method == "GET":
            return self._list_notes(request, meeting)

    def _add_note(self, request: Request, meeting: Meeting) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = Note.objects.create(
            meeting_id=meeting.id,
            author=serializer.validated_data["author"],
            text=serializer.validated_data["text"],
        )
        return Response(NoteSerializer(note).data, status=status.HTTP_201_CREATED)

    def _list_notes(self, request: Request, meeting: Meeting) -> Response:
        notes = Note.objects.filter(meeting_id=meeting.id).order_by("created_at")
        page = self.paginate_queryset(notes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="summarize",
        serializer_class=PostSummarySerializer,
    )
    def summarize(self, request: Request, pk=None) -> Response:
        meeting = self.get_object()
        summary = Summary.objects.initialize(meeting_id=meeting.id)
        notes = Note.objects.filter(meeting_id=meeting.id).order_by("created_at")
        concatenated_notes = "\n".join(note.text for note in notes)
        try:
            content = async_to_sync(ai_client.summarize)(concatenated_notes)
            summary.write(content)
            return Response(
                {"detail": "Summary created successfully."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            summary.fail(e)
            return Response(
                {"detail": "Summary creation failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        detail=True,
        methods=["get"],
        url_path="summary",
        serializer_class=SummarySerializer,
    )
    def get_summary(self, request: Request, pk=None) -> Response:
        meeting = self.get_object()
        try:
            summary = Summary.objects.get(meeting_id=meeting.id)
        except Summary.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {"detail": self.get_serializer(summary).data}, status=status.HTTP_200_OK
        )
