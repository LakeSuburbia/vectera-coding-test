---
name: tickets
description: Use this skill when the user acts as or asks you to act as a Product Owner writing/managing work items — creating a story, task, or bug ticket, adding something "to the backlog" or "to the board", or moving a ticket between kanban columns (e.g. "start VCT-3", "move VCT-5 to done").
version: 0.1.0
---

# Tickets

Write and manage minimal story/task/bug tickets with a unique ID, tracked on a lightweight kanban board. Low overhead by design — no priority, estimates, or labels unless the user explicitly asks for them.

## File layout

- `tickets/BOARD.md` — the kanban board: three columns (`To Do`, `In Progress`, `Done`), each a list of `[VCT-N](VCT-N.md) — <title>` links.
- `tickets/VCT-N.md` — one file per ticket.

If `tickets/BOARD.md` doesn't exist yet, create it first with the three empty column headings before adding any ticket.

## Ticket IDs

IDs are sequential and prefixed `VCT-` (e.g. `VCT-1`, `VCT-2`). To assign the next ID, list `tickets/*.md` (excluding `BOARD.md`), take the highest existing number, and increment. Never reuse or renumber IDs, including for deleted/abandoned tickets.

**Exception — initial setup only:** while every ticket on the board is still in `To Do` (nothing has ever moved to `In Progress` or `Done`), IDs aren't load-bearing yet and can be freely renumbered to keep them chronological, e.g. after splitting or reordering tickets. Once any ticket has left `To Do`, stop renumbering — treat IDs as fixed from that point on, per the rule above.

## Ticket template

Every ticket — story, task, or bug — uses the same shape. Only the content differs by type:

```markdown
# VCT-N: <Title>

**Type:** story | task | bug
**Status:** todo | in-progress | done

<One short paragraph. For a story: "As a <user>, I want <capability> so that <benefit>." For a task: what needs doing and why. For a bug: what's broken and how to reproduce it, in 1-3 sentences.>

**Acceptance criteria:**
- [ ] <condition that must be true to call this done — for a bug, this is the fix condition>
- [ ] <...>
```

Keep the description to one short paragraph and acceptance criteria to a handful of checkboxes. If it doesn't fit that, it's probably more than one ticket — split it rather than padding a single ticket with sections.

## Creating a ticket

1. Determine type (story/task/bug) from context — ask only if genuinely ambiguous.
2. Assign the next `VCT-N` ID.
3. Write `tickets/VCT-N.md` from the template above. Default `Status` to `todo` unless told otherwise.
4. Work out where it belongs chronologically (see "Ordering on the board" below) and insert its line at that position under the matching column in `tickets/BOARD.md` — do not just append to the bottom.
5. Confirm back to the user with the ID, title, and where it landed plus why (e.g. "VCT-7 inserted between VCT-3 and VCT-4 — depends on the endpoint VCT-3 adds"). Don't show the full ticket body unless asked.

## Ordering on the board

Every new ticket gets slotted into the chronological/dependency sequence, not tacked onto the end of a column.

- Look at the **whole board** (To Do, In Progress, Done) to figure out where the new ticket fits — what it depends on, and what would logically depend on it — even though it will only ever be inserted into its own column's list.
- New tickets land in **To Do** by default, so in practice this means finding the right position within the To Do list: after anything it depends on that's still To Do, before anything that depends on it.
- If everything it depends on is already In Progress or Done, and nothing already in To Do depends on it, it's safe to place by rough priority/logical sequence rather than a hard dependency — use judgment, don't overthink it.
- Never reorder or move tickets that already exist just to make room — only decide where the *new* one goes. If inserting it reveals that existing tickets are already in the wrong order, flag that to the user rather than silently reordering them.

## Updating status / moving on the board

1. Open the ticket file, update the `**Status:**` line.
2. Move its line in `tickets/BOARD.md` from the old column to the new one (link and title stay the same).
3. Don't rewrite the description or acceptance criteria when moving a ticket — status changes are a separate action from editing scope. If the user wants to also edit the content, treat that as an explicit separate instruction.

## What this skill does not do

No priority field, no estimates, no labels/components, no assignees, no due dates, no Backlog column separate from To Do. If the user asks for one of these repeatedly, that's a signal to revisit this skill's scope with them rather than bolting it on ad hoc for one ticket.
