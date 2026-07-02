# VCT-8: Backend API tests (happy path + validation/edge)

**Type:** task
**Status:** todo

`test_api.py` currently contains only a `pytest.mark.skip` placeholder. Replace it with a happy-path test and a validation/edge-case test covering the endpoints built in VCT-1, VCT-2, VCT-3, VCT-4, VCT-5, VCT-6.

**Acceptance criteria:**
- [ ] Happy-path test: create meeting → add note → summarize → get summary
- [ ] At least one validation/edge-case test (e.g. missing required field, or summarizing/reading an unknown meeting id)
- [ ] Skip marker removed, tests pass
