# VCT-2: Meeting create endpoint

**Type:** task
**Status:** todo

`POST /api/meetings/` on `MeetingViewSet` needs validation for required fields before it can be relied on to create meetings that notes/summaries attach to. Depends on VCT-1 (same viewset/serializer).

**Acceptance criteria:**
- [ ] `POST /api/meetings/` validates required fields (`title`, `started_at`) and returns 201 with the created meeting
- [ ] Invalid payload (e.g. missing `title`) returns 400 with field errors
