"""Unit test reproducing Issue #43 / C-03:
Agent session state is not cleared between reviews for the same user.
"""

from typing import Any, Optional
from unittest.mock import MagicMock

import pytest

from agent.memory.session_store import SessionStore
from agent.orchestrator import Orchestrator


class FakeRedis:
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self.data.get(key)

    def setex(self, key: str, ttl: int, value: Any) -> None:
        self.data[key] = value

    def delete(self, key: str) -> None:
        self.data.pop(key, None)


@pytest.mark.unit
def test_session_state_leakage_between_reviews() -> None:
    """Reproduce issue where Orchestrator.run keys session state by profile_id,
    causing stale tool results from a prior review to bleed into a new review
    for the same user profile_id.
    """
    fake_redis = FakeRedis()
    session_store = SessionStore(fake_redis)  # type: ignore[arg-type]

    # Dummy tools
    mock_github_tool = MagicMock()
    mock_github_tool.execute.return_value = MagicMock(data={"repo": "repo-A", "stars": 10})

    mock_skill_tool = MagicMock()
    mock_skill_tool.execute.return_value = MagicMock(data={"skills": ["Python"]})

    mock_market_tool = MagicMock()
    mock_market_tool.execute.return_value = MagicMock(data={"market_demand": "High"})

    tools = {
        "github_tool": mock_github_tool,
        "skill_extractor": mock_skill_tool,
        "market_analyzer": mock_market_tool,
    }

    orchestrator = Orchestrator(tools=tools, session_store=session_store)

    profile_id = "user_profile_123"

    # Review 1: User has a GitHub repo
    profile_data_1 = {
        "github_username": "alice",
        "projects": [{"github_repo": "repo-A"}],
    }
    result_1 = orchestrator.run(profile_id, profile_data_1)
    assert "github_tool" in result_1["tool_results"]

    # Session store contains review 1 results under key session:user_profile_123
    stored_state_after_run1 = session_store.get(profile_id)
    assert stored_state_after_run1 is not None
    assert "github_tool" in stored_state_after_run1

    # Review 2: Same user profile_id submits a new review with ONLY resume_text (no GitHub)
    profile_data_2 = {"resume_text": "Software Engineer with 5 years experience"}
    result_2 = orchestrator.run(profile_id, profile_data_2)
    assert "skill_extractor" in result_2["tool_results"]

    # Bug demonstration:
    # Orchestrator.run() loaded previous session_state for profile_id,
    # updated it with result_2, and persisted it back.
    # Therefore, session_store now contains stale "github_tool" from Review 1.
    stored_state_after_run2 = session_store.get(profile_id)
    assert stored_state_after_run2 is not None

    # Expected behavior: Each review should have clean session state.
    assert "github_tool" not in stored_state_after_run2, (
        "REPRODUCED BUG #43 / C-03: Stale 'github_tool' result from previous review "
        "was retained in session state for profile_id."
    )
