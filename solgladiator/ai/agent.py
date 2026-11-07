"""Autonomous AI Gladiator Agent Reasoning and Decision Engine.

Provides deep tactical game-theory heuristics, persona-driven biases,
opponent intent prediction, and combat commentary generation.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional
from solgladiator.game.models import (
    ActionType,
    GladiatorProfile,
    GladiatorClass,
    MoveDecision,
    TurnResult
)
from solgladiator.game.engine import STAMINA_COSTS
from solgladiator.ai.personas import GLADIATOR_PERSONAS


class AIGladiatorAgent:
    """Intelligent autonomous combat agent making strategic on-chain moves."""

    def __init__(self, profile: GladiatorProfile):
        self.profile = profile
        self.persona_meta = GLADIATOR_PERSONAS.get(profile.id, {})
        self.biases: Dict[ActionType, float] = self.persona_meta.get("tactical_biases", {
            ActionType.LIGHT_ATTACK: 0.25,
            ActionType.HEAVY_ATTACK: 0.25,
            ActionType.PARRY_SHIELD: 0.20,
            ActionType.ARCANE_BURST: 0.15,
            ActionType.FOCUS_RECHARGE: 0.10,
            ActionType.SURGE_STRIKE: 0.05,
        })
        self.battle_cries: List[str] = self.persona_meta.get("battle_cries", [
            "Prepare to face the wrath of the Solana Arena!",
            "For glory, for SOL, and for victory!"
        ])

    def decide_move(
        self,
        opponent: GladiatorProfile,
        history: List[TurnResult],
        current_round: int
    ) -> MoveDecision:
        """Evaluate match state and return an optimal, persona-aligned tactical move."""
        my_hp = self.profile.stats.hp
        my_stamina = self.profile.stats.stamina
        opp_hp = opponent.stats.hp
        opp_stamina = opponent.stats.stamina

        # Score candidates based on tactical situation
        scores: Dict[ActionType, float] = {action: 1.0 for action in ActionType}

        # 1. Apply baseline persona biases
        for action, bias in self.biases.items():
            scores[action] *= (1.0 + bias * 2.5)

        # 2. Hard stamina constraints & penalization
        if my_stamina < 60:
            scores[ActionType.SURGE_STRIKE] = 0.0
        if my_stamina < 45:
            scores[ActionType.ARCANE_BURST] = 0.0
        if my_stamina < 35:
            scores[ActionType.HEAVY_ATTACK] = 0.0
        if my_stamina < 15:
            scores[ActionType.LIGHT_ATTACK] = 0.0
        if my_stamina < 10:
            scores[ActionType.PARRY_SHIELD] = 0.0
            # Under 10 stamina, recharge is mandatory
            scores[ActionType.FOCUS_RECHARGE] = 100.0
        elif my_stamina < 20:
            scores[ActionType.FOCUS_RECHARGE] *= 5.0

        # If stamina is near full, recharge is wasteful
        if my_stamina >= 80:
            scores[ActionType.FOCUS_RECHARGE] = 0.01

        # 3. Predict Opponent Moves from state
        # Case A: Opponent is critically low on stamina (< 20) -> likely to FOCUS_RECHARGE
        if opp_stamina < 20:
            # When opponent recharges, they take 1.5x damage!
            scores[ActionType.HEAVY_ATTACK] *= 2.8
            scores[ActionType.LIGHT_ATTACK] *= 2.0
            scores[ActionType.SURGE_STRIKE] *= 2.2
            scores[ActionType.PARRY_SHIELD] *= 0.1  # Don't shield an empty attack

        # Case B: Opponent is high stamina and aggressive archetype -> likely to HEAVY_ATTACK
        if opp_stamina >= 40 and opponent.class_type == GladiatorClass.CYBER_BERSERKER:
            # Shield counters heavy attack into a devastating parry!
            scores[ActionType.PARRY_SHIELD] *= 2.6

        # Case C: Opponent is defensive (Sentinel) and likely to shield -> bypass with ARCANE_BURST
        if opponent.class_type == GladiatorClass.AEGIS_SENTINEL and my_stamina >= 45:
            scores[ActionType.ARCANE_BURST] *= 2.5

        # Case D: Finisher check! If opponent HP <= 35 and we have stamina for Surge or Heavy
        if opp_hp <= 35 and my_stamina >= 60:
            scores[ActionType.SURGE_STRIKE] *= 4.0
        elif opp_hp <= 25 and my_stamina >= 35:
            scores[ActionType.HEAVY_ATTACK] *= 3.0

        # Case E: Analyze recent history (last 2 rounds)
        if history:
            last_turn = history[-1]
            last_opp_action = (
                last_turn.fighter2_action if last_turn.fighter1_id == self.profile.id
                else last_turn.fighter1_action
            )
            # If opponent just parried, they rarely parry twice in a row; use Arcane or Heavy
            if last_opp_action == ActionType.PARRY_SHIELD:
                scores[ActionType.ARCANE_BURST] *= 1.8
                scores[ActionType.LIGHT_ATTACK] *= 1.4

        # 4. Softmax / Weighted Random Selection for variability
        actions = list(scores.keys())
        weights = [max(0.01, scores[a]) for a in actions]
        total_weight = sum(weights)
        probabilities = [w / total_weight for w in weights]

        # Pick move
        chosen_action: ActionType = random.choices(actions, weights=probabilities, k=1)[0]
        cost = STAMINA_COSTS.get(chosen_action, 15)

        # 5. Formulate Tactical Rationale (Explainable AI)
        rationale = self._generate_rationale(chosen_action, opp_hp, opp_stamina, my_stamina)
        battle_cry = random.choice(self.battle_cries)

        return MoveDecision(
            action=chosen_action,
            rationale=rationale,
            battle_cry=battle_cry,
            stamina_cost=cost
        )

    def _generate_rationale(
        self,
        action: ActionType,
        opp_hp: int,
        opp_stamina: int,
        my_stamina: int
    ) -> str:
        """Generate human-readable tactical reasoning for the decision."""
        if action == ActionType.SURGE_STRIKE:
            return f"Executing ultimate Surge Strike! Opponent at {opp_hp} HP is vulnerable to an on-chain execution."
        elif action == ActionType.PARRY_SHIELD:
            return f"Predicting incoming strike from opponent (stamina {opp_stamina}). Hard-light parry matrix primed."
        elif action == ActionType.ARCANE_BURST:
            return f"Target relying on armor/shields. Channeling {action.value} plasma flux to bypass defenses."
        elif action == ActionType.HEAVY_ATTACK:
            if opp_stamina < 25:
                return f"Opponent stamina depleted ({opp_stamina}). Exploiting fatigue window with heavy impact."
            return f"Offensive opening detected. Power output increased for heavy payload."
        elif action == ActionType.LIGHT_ATTACK:
            return f"Speed probe jab to disrupt opponent casting and maintain stamina efficiency ({my_stamina} remaining)."
        elif action == ActionType.FOCUS_RECHARGE:
            return f"Stamina conservation cycle: restoring 40 capacitor energy for subsequent tactical combos."
        return f"Executing optimal action {action.value} based on neural tactical evaluation."
