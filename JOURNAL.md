## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/43

**Issue title:** Agent session state is not cleared between reviews for the same user

**Tier:** [X] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
`Orchestrator.run()` (agent/orchestrator.py) keys Redis session state by `profile_id`, not per-review ID. Since `profile_id` repeats across a user's reviews, old tool results get loaded and merged into new run's results, leaking stale state forward. Fix: scope key to review/session ID, or clear state at run start.

**Branch name:** fix/43-update-agent-session-state

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger

---

## "Is this right for me?" checklist:

### Part 1 — Understanding the Issue

- [X] I can explain the problem and expected behavior in 2–3 sentences without reading the issue.
- [X] I've located the relevant files and confirmed they exist in the codebase. (`agent/orchestrator.py`, Redis session key logic)
- [X] I can describe a concrete before-and-after: what the user sees before the fix (stale tool results from a prior review bleed into a new review for the same `profile_id`) and after (each review starts with clean session state).

### Part 2 — Tier Fit

- [X] Tier is a realistic match for where I am right now. (Issue is tagged Tier 1 — self-contained, localized fix.)
- [X] This is my first open source contribution

### Part 3 — Codebase Readiness

- [X] I've found and read the specific code the issue references — not just the file, but the function/section (`Orchestrator.run()` and wherever the Redis key is built, e.g. `f"...{profile_id}..."`).
- [X] I've read enough surrounding context that I can write a rough plan for the fix without looking anything up (e.g. scope key to review/session ID vs. clear state at run start — tradeoffs of each).
- [X] I've found the test file for this module and read at least one test end-to-end (likely `tests/unit/` — orchestrator or session-state tests).

### Part 4 — Scope and Time

- [X] I've checked the issue comments and the cohort ledger's Claims count, and I'm fine with how many others are on this issue.
- [X] I've estimated the time this will take (Tier 1 → ~3–6 hrs) and I'm confident I can complete it before the Week 9 deadline.
- [X] This issue has no open blockers or dependencies on other unresolved issues.

---

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** [e3d3e08](https://github.com/AbinavRamasamy/PathReview/commit/e3d3e08)

**Reproduction summary:**
Created unit test `test_session_state_leakage_between_reviews` in `tests/unit/test_orchestrator.py`. Running `Orchestrator.run()` twice for the same `profile_id` loaded previously stored Redis session state and merged new tool execution results into it, causing stale tool results (such as `github_tool` from run 1) to bleed into run 2's session state.

**PLAN.md link:** [PLAN.md](https://github.com/AbinavRamasamy/PathReview/blob/fix/43-update-agent-session-state/PLAN.md)

**Walkthrough video (recommended):** N/A

**Blockers or open questions:**
None.
