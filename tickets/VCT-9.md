# VCT-9: CI pipeline fails on every push

**Type:** bug
**Status:** todo

`.github/workflows/ci.yml`'s only step intentionally echoes a message and exits 1, so every push and PR shows a red CI check regardless of code correctness. Repro: push any commit, open the Actions tab, see the "TODO - Setup Python and run backend tests" step fail by design.

**Acceptance criteria:**
- [ ] The placeholder "echo + exit 1" step is replaced with real steps: checkout, set up Python, install `backend/requirements.txt`, run `pytest`
- [ ] A push with passing tests produces a green CI run
- [ ] A push with a genuinely failing test produces a red CI run (the job reflects real test results, not a hardcoded outcome)
