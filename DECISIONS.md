# DECISIONS

## Overall Assumptions
- This is a dev project that is currently implemented in a way that is easy to debug, rather than a complete, production-safe implementation. If you want to change this to a production project, changes in settings.py will be needed.
- Let's assume the in-memory Summary.status can be trusted in concurrency issues. In the real world, race conditions can still happen during the write to db. But implementing this, asked for some overengineering from my side. So decided to not implement it like that.
    - Nevermind - fixed anyway. See the "Avoid concurrency issues by using a pg_lock..." entry under TUESDAY 07/07/2026 below for what was actually implemented (`_summary_lock` in `backend/meetings/models.py`).
    - Could've kept it easier for this assignment, by just using a single thread instead of overthinking it like this. But the effort was done, so decided to keep it like this.
- "Time spent" in this document is a rough estimation. I took a lot of breaks during development, since I'm currently still recovering of a concussion.

## Improvements for later
- Use a cached AI response if the notes are the same as a former request.
- Enforce type-checks using mypy.
    - Tried adding it now, but I noticed I was getting side-tracked quite badly, trying to fix typing errors. This should not be the focus right now, I think. So the current code is type-hinted, but not enforced!

## FRIDAY 03/07/2026
### Prep Work
Time spent: 30'

- Get to know the assignment & plan on how to tackle it.
- Added debug tools
    - Django Extensions -> For shell_plus access
    - "Attach to Chrome" debugger -> to debug frontend
    - "runserver" debugger -> to debug backend
    - Change pagination setting to "5" -> for easier testing / debugging
- Decided to not continue with the assignment today, due to brain fog because I'm recovering from a concussion.

## MONDAY 06/07/2026
### Backend Development
Time spent: 2h

- Bundle both notes' endpoints under a single router
    - Otherwise, this triggers a 'method not allowed' error, due to the 2 conflicting routers.
    - Another solution would be to use a single `@action` with a default handler for GET and register the POST handler separately via that action's `.mapping.post` decorator. However, since we only distinguish between 2 methods in this case, I prefer the current setup.
- Added a custom SummaryManager
    - Let's formalize & protect how we initialize Summaries.
    - Implicitly make Summary a state-machine by formalizing which actions are allowed.
- Added a custom NoteManager
    - This isn't really necessary, but I wanted to make this consistent with how we do this for the Summary model. All the info logging is done inside model & manager methods now.
- Use anthropic for a basic AI Summary tool.
    - If we would have multiple subscriptions, a more abstract implementation would make sense. For now, this will do.
    - I chose to not add fallback systems to the client, for when a call to the Anthropic API fails. But to just throw errors and let the caller handle these. In our case, we just want to set the status to failed, so we don't need more granular error handling.
    - One exception to "just throw errors": if there are no notes to summarize (empty/whitespace-only), the client returns a placeholder string ("No notes available to summarize yet.") instead of throwing, so the summary is marked ready with that placeholder rather than failed.
- I had initially written the summarize endpoint as a sync endpoint, where the async AnthropicClient method is called and awaited for inline. To make this async, I've updated this to a solution with threads. To avoid concurrency issues, I've added a pg_lock.advisory() inside `SummaryManager.initialize()` and `Summary.start()`. In a non-time-boxed context, I would go for a proper reusable queueing system instead of using threads. Maybe use python-rq?
    - I moved this new logic to the model, because it was taking up a lot of space in the views file. It's better to have this kind of logic abstracted away. An even better and scalable approach would be to create a separate 'workflow' directory with this kind of logic. It would also be good to split up the models into separate files, since the main file is growing quite a bit. But for now it's still okay, in my opinion.

## MONDAY 06/07/2026
### Front-end Development
Time spent: 30'

- Vibe coded the main chunk of the front-end code for time efficiency & lack of Angular experience.
    - This made a chronological commit history hard, so I went for a functional dependency order
    - Used a single Claude Code agent setup from the CLI.
    - Verified against the existing back-end in-browser by doing some regression testing.
    - Verified via unit tests
- Added bootstrap to give the front-end a less dry 'HTML' look.
- Changed white-space handling to pre-line for the summary overview, because newlines were being collapsed.

### DevOps
Time spent: 30'

- Added linters & formatters:
    - isort
    - black
    - eslint
- Made sure that important methods are typed.
- Added all these checks & all tests to CI.

## TUESDAY 07/07/2026
### Overall improvements
Time spent: 2h

- Used repeated manual regression testing in combination with Claude reviews to find final bugs & improvements.
    - Fixed N+1 issue by merging the Summary query with the query of the related Meeting. By using .select_related("summary")
    - Added a RUNNING status + guards for summarize()
    - Avoid concurrency issues by using a pg_lock during Summary.initialize() & Summary.start()
    - Added retries to pollSummary() following the existing polling schedule.
        - Polling runs every 2", if a request fails, we will retry after 2", with a maximum of 3 consecutive retries.
    - Minor bugfixes
    - Clear Summary content upon failure, otherwise a former "Ready" result keeps on living in the field of this "Failed" Summary.