# VCT-1: Meeting list + retrieve endpoints

**Type:** task
**Status:** todo

`MeetingViewSet`'s list/retrieve behavior needs implementing against `MeetingSerializer`: paginated newest-first listing, and retrieve including the latest summary and note count.

**Acceptance criteria:**
- [ ] `GET /api/meetings/` returns paginated results ordered newest-first (by `started_at`)
- [ ] `GET /api/meetings/:id/` includes `latest_summary` (or null) and `note_count`
- [ ] `GET /api/meetings/:id/` for an unknown id returns 404
