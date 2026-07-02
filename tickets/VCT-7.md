# VCT-7: Backend model tests

**Type:** task
**Status:** todo

`test_models.py` currently contains only a `pytest.mark.skip` placeholder. Replace it with real test(s) covering `Meeting`/`Note`/`Summary` ordering, indexing, and validation.

**Acceptance criteria:**
- [ ] Test(s) cover `Meeting` ordering (newest-first) and `Note` ordering (oldest-first)
- [ ] Test(s) exercise the `Note (meeting, created_at)` index via a normal query path
- [ ] Skip marker removed, tests pass
