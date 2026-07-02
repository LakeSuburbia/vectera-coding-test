# VCT-1: Meeting list + retrieve endpoints

**Type:** task
**Status:** in-progress
**Branch:** vct-1-meeting-list-retrieve-endpoints

`MeetingViewSet`'s list/retrieve behavior needs implementing against `MeetingSerializer`: paginated newest-first listing, and retrieve including the latest summary and note count.

**Acceptance criteria:**
- [x] `GET /api/meetings/` returns paginated results ordered newest-first (by `started_at`)
- [x] `GET /api/meetings/:id/` includes `latest_summary` (or null) and `note_count`
- [x] `GET /api/meetings/:id/` for an unknown id returns 404
