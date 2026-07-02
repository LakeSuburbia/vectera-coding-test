# VCT-14: Generate summary + status panel

**Type:** story
**Status:** todo

As a user, I want to trigger a summary of a meeting and see its current status so that I know when it's ready. Depends on VCT-5, VCT-6, VCT-12.

**Acceptance criteria:**
- [ ] "Generate summary" button on the meeting detail page calls `MeetingsService.summarize()`
- [ ] Summary panel shows current status (pending/ready/failed) and content once ready
