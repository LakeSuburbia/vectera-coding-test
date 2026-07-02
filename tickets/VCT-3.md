# VCT-3: Add note endpoint

**Type:** task
**Status:** todo

`add_note` on `MeetingViewSet` currently returns `501 Not Implemented`. Implement it so a note can be attached to a meeting. Depends on VCT-2 (need a meeting to attach notes to).

**Acceptance criteria:**
- [ ] `POST /api/meetings/:id/notes/` validates `author` + `text`, creates a `Note`, returns 201 with the serialized note
- [ ] Posting to a non-existent meeting id returns 404
