# VCT-4: List notes endpoint

**Type:** task
**Status:** todo

`list_notes` on `MeetingViewSet` currently returns `501 Not Implemented`. Implement it to return a meeting's notes in chronological order. Depends on VCT-3 (notes need to exist to be meaningfully listed).

**Acceptance criteria:**
- [ ] `GET /api/meetings/:id/notes/` returns notes for that meeting, paginated, oldest to newest
- [ ] Unknown meeting id returns 404
