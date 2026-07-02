# VCT-5: Summarize endpoint

**Type:** task
**Status:** todo

`summarize` on `MeetingViewSet` currently returns `501 Not Implemented`. Implement the simulated async flow: create/update a `Summary` as pending, concatenate the meeting's notes, call `services/ai.py::summarize`, then set the result to ready or failed, logging `meeting_id` and `note_count`. Depends on VCT-3/VCT-4 (notes need to exist to summarize).

**Acceptance criteria:**
- [ ] `POST /api/meetings/:id/summarize/` creates or updates a `Summary`, sets status pending then ready (or failed on error), and returns 202
- [ ] Summarize logs `meeting_id` and `note_count`
- [ ] Summarizing a meeting with zero notes is handled without a server error
