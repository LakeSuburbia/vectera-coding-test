import logging
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from .models import Meeting, Note, Summary
from .serializers import MeetingSerializer, NoteSerializer, SummarySerializer

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
            serializer = NoteSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="summarize")
    def summarize(self, request, pk=None):
        """
        TODO:
        - Create or update a Summary with status 'pending'
        - Simulate async job: concatenate notes, call services.ai.summarize, then set 'ready'/'failed'
        - Log meeting_id and note_count
        - Return 202 Accepted
        """
        log.info("summarize_requested", extra={"meeting_id": pk})
        return Response({"detail": "TODO: implement summarize"}, status=status.HTTP_501_NOT_IMPLEMENTED)

    @action(detail=True, methods=["get"], url_path="summary", serializer_class=SummarySerializer)
    def get_summary(self, request, pk=None):
        try:
            summary = Summary.objects.get(meeting_id=pk)
        except Summary.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": SummarySerializer(summary).data}, status=status.HTTP_200_OK)
