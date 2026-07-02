# VCT-15: Poll summary status until ready

**Type:** task
**Status:** todo

As a user, I don't want to manually refresh to see when my summary is done — the page should keep checking until it's ready or failed. Depends on VCT-14.

**Acceptance criteria:**
- [ ] While a summary is pending, the detail page polls `MeetingsService.getSummary()` on an interval
- [ ] Polling stops once status is `ready` or `failed`
