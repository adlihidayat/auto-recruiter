"""
What: State manager for an ongoing interview session.
Why: Tracks timers, turn counts, and goal progression.
Boundaries: Does not contain LLM interaction or LiveKit logic. Just purely state data.
"""

import sys
import os
import time
from typing import List, Optional
import importlib

# Ensure apps/agents is in sys.path so submodules like interviewer-agent can be found
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../agents"))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

interviewer_state = importlib.import_module("interviewer-agent.state")
Goal = interviewer_state.Goal
NextGoal = interviewer_state.NextGoal
GoalHistoryItem = interviewer_state.GoalHistoryItem
PriorGoalSummary = interviewer_state.PriorGoalSummary

class InterviewSessionState:
    """
    Tracks the complete state of a live interview session.
    """
    def __init__(self, candidate_id: str, goals: List[Goal]):
        self.candidate_id = candidate_id
        self.goals = goals
        self.current_goal_index = 0
        
        self.goal_history: List[GoalHistoryItem] = []
        self.prior_goals_summary: List[PriorGoalSummary] = []
        
        self.global_start_time = time.time()
        self.goal_start_time = time.time()
        
    @property
    def current_goal(self) -> Optional[Goal]:
        if self.current_goal_index < len(self.goals):
            return self.goals[self.current_goal_index]
        return None

    @property
    def next_goal(self) -> Optional[NextGoal]:
        if self.current_goal_index + 1 < len(self.goals):
            g = self.goals[self.current_goal_index + 1]
            return NextGoal(
                goal_id=g.goal_id,
                topic=g.topic,
                suggested_opening=g.suggested_opening
            )
        return None

    @property
    def turn_count_this_goal(self) -> int:
        # A turn is considered one candidate response.
        return sum(1 for item in self.goal_history if item.role == "candidate")

    @property
    def time_elapsed_seconds_this_goal(self) -> int:
        return int(time.time() - self.goal_start_time)

    @property
    def global_time_elapsed_seconds(self) -> int:
        return int(time.time() - self.global_start_time)

    def add_history_item(self, role: str, content: str):
        self.goal_history.append(GoalHistoryItem(role=role, content=content))

    def advance_goal(self, score_hint: str = "completed"):
        """
        Advances the session to the next goal.
        """
        if self.current_goal:
            # Add summary for the completed goal
            self.prior_goals_summary.append(PriorGoalSummary(
                goal_id=self.current_goal.goal_id,
                topic=self.current_goal.topic,
                covered=True,
                score_hint=score_hint
            ))
            
        self.current_goal_index += 1
        self.goal_history = []
        self.goal_start_time = time.time()

    def get_agent_input_state(self, latest_candidate_transcript: str) -> dict:
        """
        Formats the current state into the dict required by the interviewer-agent.
        """
        return {
            "goal": self.current_goal,
            "next_goal": self.next_goal,
            "goal_history": self.goal_history,
            "prior_goals_summary": self.prior_goals_summary,
            "latest_candidate_transcript": latest_candidate_transcript,
            "turn_count_this_goal": self.turn_count_this_goal,
            "time_elapsed_seconds_this_goal": self.time_elapsed_seconds_this_goal,
            "global_time_elapsed_seconds": self.global_time_elapsed_seconds,
            "retry_count": 0,
            "last_error": None
        }
