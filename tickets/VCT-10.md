# VCT-10: Frontend foundation — typed models + API service + routing

**Type:** task
**Status:** todo

The Angular skeleton has an empty routes array and no service/model layer. Set up typed interfaces for `Meeting`/`Note`/`Summary`, a `MeetingsService` wrapping `HttpClient` calls to `/api/meetings/...`, and route registration for `/meetings` and `/meetings/:id`, so the feature tickets below have something to build on. Depends on VCT-1, VCT-2, VCT-3, VCT-4, VCT-5, VCT-6 (needs stable endpoint contracts).

**Acceptance criteria:**
- [ ] `Meeting`, `Note`, `Summary` TypeScript interfaces match the backend serializers
- [ ] `MeetingsService` exposes methods for list, retrieve, create, add note, list notes, summarize, get summary
- [ ] Routes for `/meetings` and `/meetings/:id` are registered in `app.module.ts` (components can be placeholders at this point)
