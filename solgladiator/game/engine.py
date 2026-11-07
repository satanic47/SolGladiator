"""SolGladiator Core Combat Simulator and Damage Resolution Engine."""

from __future__ import annotations

import random
from typing import Tuple
from solgladiator.game.models import (
    ActionType,
    GladiatorProfile,
    MoveDecision,
    TurnResult,
    MatchState
)

# Stamina Costs
STAMINA_COSTS = {
    ActionType.LIGHT_ATTACK: 15,
    ActionType.HEAVY_ATTACK: 35,
    ActionType.PARRY_SHIELD: 10,
    ActionType.ARCANE_BURST: 45,
    ActionType.FOCUS_RECHARGE: -40,  # Negative cost = restores stamina
    ActionType.SURGE_STRIKE: 60,
}


class CombatEngine:
    """Deterministic, balanced combat simulation with counter mechanics and crit RNG."""

    @staticmethod
    def get_stamina_cost(action: ActionType) -> int:
        return STAMINA_COSTS.get(action, 15)

    @classmethod
    def resolve_round(
        cls,
        round_number: int,
        f1: GladiatorProfile,
        m1: MoveDecision,
        f2: GladiatorProfile,
        m2: MoveDecision
    ) -> TurnResult:
        """Resolve a single turn between two combatants simultaneously."""
        # 1. Deduct stamina or clamp if insufficient
        f1_cost = cls.get_stamina_cost(m1.action)
        f2_cost = cls.get_stamina_cost(m2.action)

        # Stamina exhaustion penalty: If fighter didn't have enough stamina, action is weakened
        f1_exhausted = False
        if f1_cost > 0 and f1.stats.stamina < f1_cost:
            f1_exhausted = True
            f1.stats.stamina = 0
        else:
            f1.stats.stamina = max(0, min(f1.stats.max_stamina, f1.stats.stamina - f1_cost))

        f2_exhausted = False
        if f2_cost > 0 and f2.stats.stamina < f2_cost:
            f2_exhausted = True
            f2.stats.stamina = 0
        else:
            f2.stats.stamina = max(0, min(f2.stats.max_stamina, f2.stats.stamina - f2_cost))

        # 2. Combat Resolution & Counters
        f1_dmg = 0
        f2_dmg = 0
        f1_crit = False
        f2_crit = False
        f1_parried = False
        f2_parried = False
        commentary = []

        # --- Fighter 1 Damage Calculation ---
        if m1.action == ActionType.LIGHT_ATTACK:
            base = f1.stats.attack * 0.8
            f1_dmg = max(8, int(base - f2.stats.defense * 0.3))
            if m2.action == ActionType.PARRY_SHIELD:
                f1_dmg = int(f1_dmg * 0.4)
                commentary.append(f"{f2.name}'s shield partially deflected {f1.name}'s light jab.")
            elif m2.action == ActionType.FOCUS_RECHARGE:
                f1_dmg = int(f1_dmg * 1.5)
                commentary.append(f"{f1.name} interrupted {f2.name}'s focus with a swift jab!")

        elif m1.action == ActionType.HEAVY_ATTACK:
            if m2.action == ActionType.PARRY_SHIELD:
                # Countered! F2 parries F1
                f1_parried = True
                f1_dmg = 0
                counter_dmg = int(f2.stats.attack * 0.7)
                f2_dmg += counter_dmg
                commentary.append(f"PERFECT PARRY! {f2.name} deflected {f1.name}'s heavy swing and riposted for {counter_dmg} damage!")
            else:
                base = f1.stats.attack * 1.5
                f1_dmg = max(18, int(base - f2.stats.defense * 0.4))
                if m2.action == ActionType.FOCUS_RECHARGE:
                    f1_dmg = int(f1_dmg * 1.6)
                    commentary.append(f"{f1.name} crushed {f2.name} during recharge!")

        elif m1.action == ActionType.ARCANE_BURST:
            base = f1.stats.attack * 1.35
            f1_dmg = int(base)  # Arcane damage ignores physical defense
            if m2.action == ActionType.PARRY_SHIELD:
                f1_dmg = int(f1_dmg * 1.25)
                commentary.append(f"{f1.name}'s Arcane Burst shattered straight through {f2.name}'s shield!")

        elif m1.action == ActionType.SURGE_STRIKE:
            base = f1.stats.attack * 2.2
            f1_dmg = max(35, int(base - f2.stats.defense * 0.2))
            commentary.append(f"CRITICAL SURGE! {f1.name} unleashed a devastating finisher!")

        elif m1.action == ActionType.FOCUS_RECHARGE:
            commentary.append(f"{f1.name} centered their breathing and recharged +40 stamina.")

        # --- Fighter 2 Damage Calculation ---
        if m2.action == ActionType.LIGHT_ATTACK:
            base = f2.stats.attack * 0.8
            f2_dmg_dealt = max(8, int(base - f1.stats.defense * 0.3))
            if m1.action == ActionType.PARRY_SHIELD:
                f2_dmg_dealt = int(f2_dmg_dealt * 0.4)
                commentary.append(f"{f1.name}'s shield partially deflected {f2.name}'s light jab.")
            elif m1.action == ActionType.FOCUS_RECHARGE:
                f2_dmg_dealt = int(f2_dmg_dealt * 1.5)
                commentary.append(f"{f2.name} interrupted {f1.name}'s focus with a swift jab!")
            f2_dmg += f2_dmg_dealt

        elif m2.action == ActionType.HEAVY_ATTACK:
            if m1.action == ActionType.PARRY_SHIELD:
                # F1 parries F2
                f2_parried = True
                counter_dmg = int(f1.stats.attack * 0.7)
                f1_dmg += counter_dmg
                commentary.append(f"PERFECT PARRY! {f1.name} deflected {f2.name}'s heavy strike and countered for {counter_dmg} damage!")
            else:
                base = f2.stats.attack * 1.5
                f2_dmg_dealt = max(18, int(base - f1.stats.defense * 0.4))
                if m1.action == ActionType.FOCUS_RECHARGE:
                    f2_dmg_dealt = int(f2_dmg_dealt * 1.6)
                    commentary.append(f"{f2.name} pulverized {f1.name} during recharge!")
                f2_dmg += f2_dmg_dealt

        elif m2.action == ActionType.ARCANE_BURST:
            base = f2.stats.attack * 1.35
            f2_dmg_dealt = int(base)
            if m1.action == ActionType.PARRY_SHIELD:
                f2_dmg_dealt = int(f2_dmg_dealt * 1.25)
                commentary.append(f"{f2.name}'s Arcane Burst shattered straight through {f1.name}'s shield!")
            f2_dmg += f2_dmg_dealt

        elif m2.action == ActionType.SURGE_STRIKE:
            base = f2.stats.attack * 2.2
            f2_dmg_dealt = max(35, int(base - f1.stats.defense * 0.2))
            f2_dmg += f2_dmg_dealt
            commentary.append(f"CRITICAL SURGE! {f2.name} unleashed an almighty strike!")

        elif m2.action == ActionType.FOCUS_RECHARGE:
            commentary.append(f"{f2.name} entered a meditative state, regaining +40 stamina.")

        # Exhaustion reduction
        if f1_exhausted and f1_dmg > 0:
            f1_dmg = max(5, int(f1_dmg * 0.4))
            commentary.append(f"{f1.name} was gasping for stamina, severely weakening their blow.")
        if f2_exhausted and f2_dmg > 0:
            f2_dmg = max(5, int(f2_dmg * 0.4))
            commentary.append(f"{f2.name} was out of breath, weakening their impact.")

        # Critical Hit Checks
        if f1_dmg > 0 and random.random() < f1.stats.crit_rate:
            f1_crit = True
            f1_dmg = int(f1_dmg * 1.5)
            commentary.append(f"⚡ CRITICAL HIT from {f1.name}!")
        if f2_dmg > 0 and random.random() < f2.stats.crit_rate:
            f2_crit = True
            f2_dmg = int(f2_dmg * 1.5)
            commentary.append(f"⚡ CRITICAL HIT from {f2.name}!")

        # Apply damage
        f1.stats.hp = max(0, f1.stats.hp - f2_dmg)
        f2.stats.hp = max(0, f2.stats.hp - f1_dmg)

        if not commentary:
            commentary.append(f"Round {round_number}: Combatants traded blows across the cyber arena.")

        return TurnResult(
            round_number=round_number,
            fighter1_id=f1.id,
            fighter1_action=m1.action,
            fighter1_damage_dealt=f1_dmg,
            fighter1_stamina_delta=-f1_cost,
            fighter1_battle_cry=m1.battle_cry,
            fighter1_rationale=m1.rationale,
            fighter2_id=f2.id,
            fighter2_action=m2.action,
            fighter2_damage_dealt=f2_dmg,
            fighter2_stamina_delta=-f2_cost,
            fighter2_battle_cry=m2.battle_cry,
            fighter2_rationale=m2.rationale,
            round_commentary=" ".join(commentary),
            is_fighter1_crit=f1_crit,
            is_fighter2_crit=f2_crit,
            fighter1_parried=f1_parried,
            fighter2_parried=f2_parried,
            fighter1_hp_remaining=f1.stats.hp,
            fighter2_hp_remaining=f2.stats.hp,
            fighter1_stamina_remaining=f1.stats.stamina,
            fighter2_stamina_remaining=f2.stats.stamina
        )
