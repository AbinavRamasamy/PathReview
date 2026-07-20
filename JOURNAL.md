## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/43

**Issue title:** Agent session state is not cleared between reviews for the same user

**Tier:** [X] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
`Orchestrator.run()` (agent/orchestrator.py) keys Redis session state by `profile_id`, not per-review ID. Since `profile_id` repeats across a user's reviews, old tool results get loaded and merged into new run's results, leaking stale state forward. Fix: scope key to review/session ID, or clear state at run start.

**Branch name:** fix/43-update-agent-session-state

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger
