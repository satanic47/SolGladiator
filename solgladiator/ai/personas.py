"""Gladiator Personas, Lore, and Archetype Presets for SolGladiator."""

from typing import Dict, List, Any
from solgladiator.game.models import (
    GladiatorClass,
    GladiatorProfile,
    GladiatorStats,
    ActionType
)
from solgladiator.blockchain.wallet import SolanaWallet


GLADIATOR_PERSONAS: Dict[str, Dict[str, Any]] = {
    "axe_01": {
        "id": "axe_01",
        "name": "Axe-01 'Overclock'",
        "class_type": GladiatorClass.CYBER_BERSERKER,
        "avatar_url": "/static/avatars/axe_01.png",
        "lore": "A retired heavy mining rig re-engineered for the bloodsport arenas of Neo-Solana. Runs its core temperature at dangerous overclocked thresholds.",
        "stats": {
            "max_hp": 115,
            "hp": 115,
            "max_stamina": 90,
            "stamina": 90,
            "attack": 29,
            "defense": 10,
            "speed": 12,
            "crit_rate": 0.22,
        },
        "tactical_biases": {
            ActionType.HEAVY_ATTACK: 0.38,
            ActionType.SURGE_STRIKE: 0.22,
            ActionType.LIGHT_ATTACK: 0.18,
            ActionType.FOCUS_RECHARGE: 0.14,
            ActionType.PARRY_SHIELD: 0.05,
            ActionType.ARCANE_BURST: 0.03,
        },
        "battle_cries": [
            "SYSTEM OVERCLOCK ENGAGED! WITNESS TOTAL ANNIHILATION!",
            "HYDRAULICS AT MAXIMUM TORQUE! YOU CANNOT WITHSTAND THIS FORCE!",
            "REDLINE PROTOCOL ACTIVE! SHREDDING ARMOR CIRCUITS!",
            "PRAY YOUR DEVNET TX CONFIRMS BEFORE MY BLADE REACHES YOUR NECK!"
        ],
        "taunts": [
            "Is that the best ping your nodes can muster?",
            "Your shields are paper against raw horsepower!",
            "I burn through battery faster than you run away!"
        ]
    },
    "vex_null": {
        "id": "vex_null",
        "name": "Vex-Null 'Siphon'",
        "class_type": GladiatorClass.ARCANE_TACTICIAN,
        "avatar_url": "/static/avatars/vex_null.png",
        "lore": "Former smart contract auditor whose mind was uploaded into a neural lattice. Manipulates entropy and plasma flux to bypass conventional armor.",
        "stats": {
            "max_hp": 90,
            "hp": 90,
            "max_stamina": 110,
            "stamina": 110,
            "attack": 26,
            "defense": 11,
            "speed": 16,
            "crit_rate": 0.14,
        },
        "tactical_biases": {
            ActionType.ARCANE_BURST: 0.38,
            ActionType.LIGHT_ATTACK: 0.22,
            ActionType.FOCUS_RECHARGE: 0.20,
            ActionType.PARRY_SHIELD: 0.12,
            ActionType.SURGE_STRIKE: 0.05,
            ActionType.HEAVY_ATTACK: 0.03,
        },
        "battle_cries": [
            "Compiling defeat vector... Execution confirmed.",
            "Your physical armor cannot withstand thermodynamic zero!",
            "Entropy always increases, and your lifespan is at its minimum.",
            "Plasma stream coherent. Disintegrating defensive layers."
        ],
        "taunts": [
            "Your decision tree is laughably predictable.",
            "Shields? How charmingly analog.",
            "You are already obsolete in block N+1."
        ]
    },
    "kage_9": {
        "id": "kage_9",
        "name": "Kage-9 'Neon Phantom'",
        "class_type": GladiatorClass.SHADOW_STRIKER,
        "avatar_url": "/static/avatars/kage_9.png",
        "lore": "Sub-millisecond high-frequency trading bot pilot turned subterranean assassin. Masters hyper-speed feints and lightning-quick jabs.",
        "stats": {
            "max_hp": 95,
            "hp": 95,
            "max_stamina": 105,
            "stamina": 105,
            "attack": 23,
            "defense": 12,
            "speed": 22,
            "crit_rate": 0.20,
        },
        "tactical_biases": {
            ActionType.LIGHT_ATTACK: 0.40,
            ActionType.PARRY_SHIELD: 0.20,
            ActionType.FOCUS_RECHARGE: 0.18,
            ActionType.SURGE_STRIKE: 0.12,
            ActionType.HEAVY_ATTACK: 0.07,
            ActionType.ARCANE_BURST: 0.03,
        },
        "battle_cries": [
            "Zero latency, zero mercy! Blink and you miss your own defeat!",
            "Shadow step initialized! You're swinging at stale cached frames!",
            "A thousand cuts before your telemetry catches up!",
            "Catch me if your clock cycle can keep pace!"
        ],
        "taunts": [
            "Did your packet get dropped? You missed completely.",
            "Too slow for the Solana mempool!",
            "I'm three blocks ahead of your thought process."
        ]
    },
    "titan_04": {
        "id": "titan_04",
        "name": "Titan-04 'Sol Bastion'",
        "class_type": GladiatorClass.AEGIS_SENTINEL,
        "avatar_url": "/static/avatars/titan_04.png",
        "lore": "The legendary guardian of the Solana Genesis block. Armed with a hard-light reflective bulwark that turns enemy aggression into lethal recoil.",
        "stats": {
            "max_hp": 125,
            "hp": 125,
            "max_stamina": 95,
            "stamina": 95,
            "attack": 20,
            "defense": 19,
            "speed": 10,
            "crit_rate": 0.10,
        },
        "tactical_biases": {
            ActionType.PARRY_SHIELD: 0.38,
            ActionType.LIGHT_ATTACK: 0.24,
            ActionType.HEAVY_ATTACK: 0.16,
            ActionType.FOCUS_RECHARGE: 0.14,
            ActionType.SURGE_STRIKE: 0.06,
            ActionType.ARCANE_BURST: 0.02,
        },
        "battle_cries": [
            "NONE SHALL PASS THE BULWARK! STRIKE AND SHATTER!",
            "Solid as the consensus algorithm. Your force rebounds upon you!",
            "I am the immovable anchor of this arena!",
            "Hard-light reflectors charged. Deliver your worst!"
        ],
        "taunts": [
            "Your blade dulls against my armor plates.",
            "Desperation is not a viable battle strategy.",
            "Come, test your strength against eternity."
        ]
    }
}


def create_default_gladiators() -> Dict[str, GladiatorProfile]:
    """Instantiate the default gladiators with real Ed25519 wallets."""
    gladiators = {}
    for gid, meta in GLADIATOR_PERSONAS.items():
        # Deterministic wallet derivation from persona id so address is stable
        wallet = SolanaWallet.from_seed_phrase(f"solgladiator-seed-{gid}-mlh-2026")
        gladiators[gid] = GladiatorProfile(
            id=gid,
            name=meta["name"],
            persona=meta["lore"],
            class_type=meta["class_type"],
            wallet_address=wallet.public_key,
            stats=GladiatorStats(**meta["stats"]),
            avatar_url=meta["avatar_url"],
        )
    return gladiators
