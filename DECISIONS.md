# DECISIONS

Briefly note:
- Key choices you made & trade-offs.
- Deviations from the initial spec (if any) and why.
- Next improvements you'd make if you had more time.
- Time spent per area.

Overall Assumptions:
- This is a dev project that is currently implemented in a way that is easy to debug, rather than a complete, production-safe implementation.

FRIDAY 03/07/2026
Prep Work
Time spent: 30'

- Get to know the assignment & plan on how to tackle it.
- Added debug tools
    - Django Extensions -> For shell_plus access
    - "Attach to Chrome" debugger -> to debug frontend
    - "runserver" debugger -> to debug backend
    - Change pagination setting to "5" -> for easier testing / debugging
- Decided to not continue with the assignment today, due to brain fog because I'm recovering from a concussion.

MONDAY 06/07/2026
Backend Development
Time spent: 2h

- Bundle both notes' endpoints under a single router
    - Otherwise, this triggers a 'method not allowed' error, due to the 2 conflicting routers.
    - Another solution would be to use a default view for the get method and add other views using get_notes.mapping.<method>. However, since we only distinguish between 2 methods in this case, I prefer the current setup.
- Added a custom SummaryManager
    - Let's formalize & protect how we initialize Summaries.
    - Implicitly make Summary a state-machine by formalizing which actions are allowed.
- Added a custom NoteManager
    - This isn't really necessary, but I wanted to make this consistent with how we do this for the Summary model. All the info logging is done inside the scope of the model methods.
- Use anthropic for a basic AI Summary tool.
    - If we would have multiple subscriptions, a more abstract implementation would make sense. For now, this will do.
    - I chose to not add fallback systems to the client, for when a call to the Anthropic API fails. But to just throw errors and let the caller handle these. In our case, we just want to set the status to failed, so we don't need more granular error handling.