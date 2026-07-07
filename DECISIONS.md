# DECISIONS

Briefly note:
- Key choices you made & trade-offs.
- Deviations from the initial spec (if any) and why.
- Next improvements you'd make if you had more time.
- Time spent per area.

Overall Assumptions:
- This is a dev project that is currently implemented in a way that is easy to debug, rather than a complete, production-safe implementation. If you want to change this to a production project, changes in settings.py will be needed.
- Let's assume the in-memory Summary.status can be trusted in concurrency issues. In the real world, race conditions can still happen during the write to db. But implementing this, asked for some overengineering from my side. So decided to not implement it like that.
    - Nevermind, fixed it anyway.

Improvements for later:
- Use a cached AI response if the notes are the same as a former request.
- Enforce type-checks using mypy.
    - Tried adding it now, but I noticed I was getting side-tracked quite badly, trying to fix typing errors. This should not be the focus right now, I think. So the current code is type-hinted, but not enforced!

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
    - One exception to "just throw errors": if there are no notes to summarize (empty/whitespace-only), the client returns a placeholder string ("No notes available to summarize yet.") instead of throwing, so the summary is marked ready with that placeholder rather than failed.
- I had initially written the summarize endpoint as a sync endpoint, where the async AnthropicClient method is called and awaited for inline. To make this async, I've updated this to a solution with threads. To avoid concurrency issues, I've added a a pg_lock.advisory() to _run_summary_job. In a non-time-boxed context, I would go for a proper reusable queueing system instead of using threads. Maybe use python-rq?
    - I moved this new logic to the model, because it was taking up a lot of space in the views file. It's better to have this kind of logic abstracted away. An even better and scalable approach would be to create a seperate 'workflow' directory with this kind of logic. It would also be good to split up the models into seperate files, since the main file is growing quite a bit. But for now it's still okay, in my opinion.

MONDAY 06/07/2026
Front-end Development
Time-spent: 1h

- Vibe coded the main chunk of the front-end code for time efficiëncy & lack of Angular experience.
    - This made a chronological commit history hard, so I went for a functional dependency order
    - Used a single Claude Code agent setup from the CLI.
    - Verified against the existing back-end in-browser by doing some regression testing.
    - Verified via unit tests
- Added bootstrap to give the front-end a less dry 'HTML' look.
- Changed white-space handling to pre-line for the summary overview, because newlines were being collapsed.

MONDAY 06/07/2026
DevOps
Time-spent: 1h

- Added linters & formatters:
    - isort
    - black
    - eslint
- Made sure that important methods are typed.
- Added all these checks & all tests to CI.

TUESDAY 07/07/2026
Overall improvements
Time-spent: 1h

- Fix N+1 issue
- Added a RUNNING status + basic in-memory guards for
summarize()
- Avoid concurrency by using a pg_lock during Summary.initialize() & Summary.start()
- Small bugfixes