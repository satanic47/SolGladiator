"""Unit Tests for Combat Mechanics, Engine Counter-Play, and Boundary Conditions."""

import pytest
from solgladiator.game.models import (
    ActionType,
    GladiatorProfile,
    GladiatorStats,
    GladiatorClass,
    MoveDecision
)
from solgladiator.game.engine import CombatEngine
from solgladiator.game.arena import ArenaDuelMatch


@pytest.fixture
def fighters():
    f1 = GladiatorProfile(
        id="f1",
        name="Striker 1",
        persona="Test combatant 1",
        class_type=GladiatorClass.CYBER_BERSERKER,
        wallet_address="11111111111111111111111111111111",
        stats=GladiatorStats(max_hp=100, hp=100, max_stamina=100, stamina=100, attack=30, defense=10)
    )
    f2 = GladiatorProfile(
        id="f2",
        name="Defender 2",
        persona="Test combatant 2",
        class_type=GladiatorClass.AEGIS_SENTINEL,
        wallet_address="22222222222222222222222222222222",
        stats=GladiatorStats(max_hp=100, hp=100, max_stamina=100, stamina=100, attack=20, defense=18)
    )
    return f1, f2


def test_parry_counters_heavy_attack(fighters):
    f1, f2 = fighters
    m1 = MoveDecision(action=ActionType.HEAVY_ATTACK, rationale="Heavy swing", battle_cry="Smash!")
    m2 = MoveDecision(action=ActionType.PARRY_SHIELD, rationale="Parry", battle_cry="Blocked!")

    res = CombatEngine.resolve_round(1, f1, m1, f2, m2)

    assert res.fighter1_parried is True
    assert res.fighter1_damage_dealt == 0
    # Parry reflects damage back onto attacker
    assert res.fighter2_damage_dealt > 0
    assert f1.stats.hp < 100
    assert f2.stats.hp == 100


def test_arcane_burst_bypasses_shield(fighters):
    f1, f2 = fighters
    m1 = MoveDecision(action=ActionType.ARCANE_BURST, rationale="Arcane blast", battle_cry="Magic!")
    m2 = MoveDecision(action=ActionType.PARRY_SHIELD, rationale="Parry", battle_cry="Shield!")

    res = CombatEngine.resolve_round(1, f1, m1, f2, m2)

    assert res.fighter1_damage_dealt > 0
    # Arcane pierces right through shield
    assert f2.stats.hp < 100


def test_focus_recharge_restores_stamina(fighters):
    f1, f2 = fighters
    f1.stats.stamina = 20
    m1 = MoveDecision(action=ActionType.FOCUS_RECHARGE, rationale="Restoring", battle_cry="Recharge!")
    m2 = MoveDecision(action=ActionType.PARRY_SHIELD, rationale="Guarding", battle_cry="Guard!")

    res = CombatEngine.resolve_round(1, f1, m1, f2, m2)

    assert f1.stats.stamina > 20
    assert res.fighter1_stamina_delta == 40


def test_recharge_interrupted_by_strike_takes_extra_damage(fighters):
    f1, f2 = fighters
    m1 = MoveDecision(action=ActionType.LIGHT_ATTACK, rationale="Quick poke", battle_cry="Poke!")
    m2 = MoveDecision(action=ActionType.FOCUS_RECHARGE, rationale="Recharging", battle_cry="Charge!")

    res = CombatEngine.resolve_round(1, f1, m1, f2, m2)

    # 1.5x bonus damage applied for catching opponent recharging
    assert res.fighter1_damage_dealt > 15
    assert f2.stats.hp < 85


def test_exhaustion_penalty_when_stamina_depleted(fighters):
    f1, f2 = fighters
    f1.stats.stamina = 5  # Too low for HEAVY_ATTACK (needs 35)

    m1 = MoveDecision(action=ActionType.HEAVY_ATTACK, rationale="Desperate swing", battle_cry="Ugh!")
    m2 = MoveDecision(action=ActionType.PARRY_SHIELD, rationale="Block", battle_cry="Ha!")

    res = CombatEngine.resolve_round(1, f1, m1, f2, m2)
    # Stamina should be clamped to 0
    assert f1.stats.stamina == 0


def test_match_post_game_over_turn_rejection(fighters):
    f1, f2 = fighters
    match = ArenaDuelMatch(f1, f2, wager_sol=0.05)

    # Force game over by killing fighter 2
    match.fighter2.stats.hp = 0
    m1 = MoveDecision(action=ActionType.LIGHT_ATTACK, rationale="Poke", battle_cry="Done!")
    m2 = MoveDecision(action=ActionType.LIGHT_ATTACK, rationale="Poke", battle_cry="Done!")

    # Resolve one turn to trigger game over
    match.execute_turn(m1, m2)
    assert match.is_game_over is True

    # Next attempt to execute a turn must be rejected
    with pytest.raises(ValueError, match="already concluded"):
        match.execute_turn(m1, m2)


def test_max_rounds_tiebreak(fighters):
    f1, f2 = fighters
    match = ArenaDuelMatch(f1, f2, wager_sol=0.05)
    match.max_rounds = 2
    match.fighter1.stats.hp = 90
    match.fighter2.stats.hp = 40  # F1 has significantly more HP

    m1 = MoveDecision(action=ActionType.PARRY_SHIELD, rationale="Shield", battle_cry="Hold")
    m2 = MoveDecision(action=ActionType.PARRY_SHIELD, rationale="Shield", battle_cry="Hold")

    match.execute_turn(m1, m2)
    match.execute_turn(m1, m2)

    assert match.is_game_over is True
    assert match.winner_id == f1.id
