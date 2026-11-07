"""Unit Tests for AI Gladiator Agent Reasoning and Decision Making."""

import pytest
from solgladiator.game.models import ActionType
from solgladiator.ai.personas import create_default_gladiators
from solgladiator.ai.agent import AIGladiatorAgent


def test_ai_agent_initialization():
    glads = create_default_gladiators()
    berserker = glads["axe_01"]
    agent = AIGladiatorAgent(berserker)

    assert agent.profile.id == "axe_01"
    assert ActionType.HEAVY_ATTACK in agent.biases
    assert len(agent.battle_cries) > 0


def test_ai_agent_low_stamina_recharge_priority():
    glads = create_default_gladiators()
    berserker = glads["axe_01"]
    sentinel = glads["titan_04"]

    # Starve stamina
    berserker.stats.stamina = 5
    agent = AIGladiatorAgent(berserker)

    decision = agent.decide_move(sentinel, [], 1)

    # Agent should heavily prioritize recharge when out of stamina
    assert decision.action == ActionType.FOCUS_RECHARGE
    assert "stamina" in decision.rationale.lower() or "energy" in decision.rationale.lower()


def test_ai_agent_generates_rationale_and_battle_cry():
    glads = create_default_gladiators()
    f1 = glads["kage_9"]
    f2 = glads["vex_null"]
    agent = AIGladiatorAgent(f1)

    decision = agent.decide_move(f2, [], 1)

    assert decision.action in ActionType
    assert len(decision.rationale) > 10
    assert len(decision.battle_cry) > 5
