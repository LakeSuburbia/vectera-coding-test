# VCT-6: Get summary endpoint

**Type:** task
**Status:** todo

`get_summary` on `MeetingViewSet` currently returns `501 Not Implemented`. Implement it to return the current summary for a meeting. Depends on VCT-5 (a summary needs to be creatable first).

**Acceptance criteria:**
- [ ] `GET /api/meetings/:id/summary/` returns the current summary
- [ ] Returns 404 if no summary exists yet for that meeting
