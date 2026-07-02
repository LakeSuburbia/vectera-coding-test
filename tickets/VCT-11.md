# VCT-11: Meetings list page

**Type:** story
**Status:** todo

As a user, I want to see a list of all meetings (title, started at, note count, summary badge) so that I can pick one to open. Depends on VCT-1, VCT-10.

**Acceptance criteria:**
- [ ] `/meetings` route renders a list fetched via `MeetingsService.list()`
- [ ] Each row shows title, `started_at`, `note_count`, and a summary status badge (pending/ready/failed/none)
- [ ] Loading and error states are shown while/if the request is in flight or fails
