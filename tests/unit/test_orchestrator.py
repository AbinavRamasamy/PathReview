"""Tests for orchestrator.py"""

from unittest.mock import MagicMock

import pytest

from agent.memory.session_store import SessionStore
from agent.orchestrator import Orchestrator


class FakeRedis:
    """Fake Redis client for unit testing."""

    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def setex(self, key, ttl, value):
        self.data[key] = value

    def delete(self, key):
        self.data.pop(key, None)


@pytest.mark.unit
class TestOrchestrator:
    """Test suite for Orchestrator."""

    @pytest.fixture
    def session_store(self):
        """Create a SessionStore backed by FakeRedis."""
        fake_redis = FakeRedis()
        return SessionStore(fake_redis)

    @pytest.fixture
    def orchestrator(self, session_store):
        """Create an Orchestrator with mock tools and session store."""
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
        return Orchestrator(tools=tools, session_store=session_store)

    def test_session_state_not_cleared_between_reviews(self, orchestrator, session_store):
        """Test that agent session state is not cleared between reviews for the same user (reproduces Issue #43)."""
        profile_id = "user_profile_123"

        # First review: profile contains a GitHub repo
        profile_data_1 = {
            "github_username": "alice",
            "projects": [{"github_repo": "repo-A"}],
        }
        result_1 = orchestrator.run(profile_id, profile_data_1)
        assert "github_tool" in result_1["tool_results"]

        # Verify state was saved to session store
        stored_state_after_run1 = session_store.get(profile_id)
        assert stored_state_after_run1 is not None
        assert "github_tool" in stored_state_after_run1

        # Second review: same user profile_id submits a new review with only resume text
        profile_data_2 = {"resume_text": "Software Engineer with 5 years experience"}
        result_2 = orchestrator.run(profile_id, profile_data_2)
        assert "skill_extractor" in result_2["tool_results"]

        # Session state after second run
        stored_state_after_run2 = session_store.get(profile_id)
        assert stored_state_after_run2 is not None

        # Bug assertion: Each review should start with clean session state
        assert "github_tool" not in stored_state_after_run2, (
            "REPRODUCED BUG #43 / C-03: Stale 'github_tool' result from previous review "
            "was retained in session state for profile_id."
        )
