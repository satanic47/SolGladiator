"""Game Data Models and Schemas for SolGladiator."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Combat actions available to gladiators."""
    LIGHT_ATTACK = "LIGHT_ATTACK"        # Quick strike, low stamina cost (15), reliable hit
    HEAVY_ATTACK = "HEAVY_ATTACK"        # Heavy hit, moderate cost (35), can be parried
    PARRY_SHIELD = "PARRY_SHIELD"        # Defensive block (10 cost), reflects heavy attacks
    ARCANE_BURST = "ARCANE_BURST"        # Magic damage bypasses shields, high cost (45)
    FOCUS_RECHARGE = "FOCUS_RECHARGE"    # Regains 40 stamina, takes 1.5x damage if struck
    SURGE_STRIKE = "SURGE_STRIKE"        # Ultimate finisher, requires >= 60 stamina


class GladiatorClass(str, Enum):
    """Character archetypes with distinct combat modifiers."""
    CYBER_BERSERKER = "CYBER_BERSERKER"      # High raw power and crit, lower defense
    ARCANE_TACTICIAN = "ARCANE_TACTICIAN"    # High mana/stamina regeneration, deadly bursts
    SHADOW_STRIKER = "SHADOW_STRIKER"        # High speed and dodge, swift multi-strikes
    AEGIS_SENTINEL = "AEGIS_SENTINEL"        # Heavy armor, superior parry and counter


class GladiatorStats(BaseModel):
    """Combat attributes of a gladiator."""
    max_hp: int = 100
    hp: int = 100
    max_stamina: int = 100
    stamina: int = 100
    attack: int = 24
    defense: int = 12
    speed: int = 15
    crit_rate: float = 0.15  # 15% chance to crit


class GladiatorProfile(BaseModel):
    """Complete gladiator identity and wallet pairing."""
    id: str
    name: str
    persona: str
    class_type: GladiatorClass
    wallet_address: str
    stats: GladiatorStats
    avatar_url: Optional[str] = None


class MoveDecision(BaseModel):
    """The tactical choice produced by an AI or human combatant."""
    action: ActionType
    rationale: str
    battle_cry: str
    stamina_cost: int = 0


class TurnResult(BaseModel):
    """Detailed resolution of one combat exchange."""
    round_number: int
    fighter1_id: str
    fighter1_action: ActionType
    fighter1_damage_dealt: int
    fighter1_stamina_delta: int
    fighter1_battle_cry: str
    fighter1_rationale: str

    fighter2_id: str
    fighter2_action: ActionType
    fighter2_damage_dealt: int
    fighter2_stamina_delta: int
    fighter2_battle_cry: str
    fighter2_rationale: str

    round_commentary: str
    is_fighter1_crit: bool = False
    is_fighter2_crit: bool = False
    fighter1_parried: bool = False
    fighter2_parried: bool = False

    fighter1_hp_remaining: int
    fighter2_hp_remaining: int
    fighter1_stamina_remaining: int
    fighter2_stamina_remaining: int


class MatchState(BaseModel):
    """Live state of an arena duel."""
    match_id: str
    fighter1: GladiatorProfile
    fighter2: GladiatorProfile
    current_round: int = 0
    max_rounds: int = 20
    is_game_over: bool = False
    winner_id: Optional[str] = None
    loser_id: Optional[str] = None
    history: List[TurnResult] = Field(default_factory=list)
    escrow: Optional[Dict[str, Any]] = None
