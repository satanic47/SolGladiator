"""Security & Exploit Vulnerability Tests for SolGladiator."""

import pytest
from solgladiator.blockchain.wallet import SolanaWallet
from solgladiator.blockchain.escrow import DuelEscrowVault, EscrowSecurityError
from solgladiator.game.models import (
    ActionType,
    GladiatorProfile,
    GladiatorStats,
    GladiatorClass,
    MoveDecision
)
from solgladiator.game.engine import CombatEngine


@pytest.fixture
def wallets():
    f1 = SolanaWallet.generate()
    f2 = SolanaWallet.generate()
    arbiter = SolanaWallet.generate()
    return f1, f2, arbiter


def test_replay_attack_double_settlement_rejected(wallets):
    f1, f2, arbiter = wallets
    vault = DuelEscrowVault(arbiter_wallet=arbiter)
    match_id = "sec_match_replay_01"

    vault.create_match_escrow(match_id, f1, f2, wager_sol=0.1)

    # First settlement succeeds
    vault.settle_match_escrow(match_id, f1.public_key, {"rounds": 3, "winner": "f1"})

    # Second settlement attempt MUST fail with EscrowSecurityError (Replay protection)
    with pytest.raises(EscrowSecurityError, match="Replay attack prevented"):
        vault.settle_match_escrow(match_id, f1.public_key, {"rounds": 3, "winner": "f1"})


def test_unauthorized_winner_drain_rejected(wallets):
    f1, f2, arbiter = wallets
    attacker = SolanaWallet.generate()
    vault = DuelEscrowVault(arbiter_wallet=arbiter)
    match_id = "sec_match_unauth_02"

    vault.create_match_escrow(match_id, f1, f2, wager_sol=0.1)

    # Attacker tries to claim the escrow pot without participating in the match
    with pytest.raises(EscrowSecurityError, match="Unauthorized winner"):
        vault.settle_match_escrow(match_id, attacker.public_key, {"rounds": 2, "winner": "attacker"})


def test_wager_out_of_bounds_rejected(wallets):
    f1, f2, arbiter = wallets
    vault = DuelEscrowVault(arbiter_wallet=arbiter)

    # Zero or negative wager
    with pytest.raises(EscrowSecurityError, match="outside secure bounds"):
        vault.create_match_escrow("bad_wager_1", f1, f2, wager_sol=0.0)

    # Exorbitant wager over max limit
    with pytest.raises(EscrowSecurityError, match="outside secure bounds"):
        vault.create_match_escrow("bad_wager_2", f1, f2, wager_sol=999.0)


def test_tampered_duel_digest_verification_fails(wallets):
    f1, f2, arbiter = wallets
    vault = DuelEscrowVault(arbiter_wallet=arbiter)
    match_id = "sec_audit_proof_03"

    vault.create_match_escrow(match_id, f1, f2, wager_sol=0.05)
    receipt = vault.settle_match_escrow(match_id, f1.public_key, {"winner": "f1", "rounds": 5})

    # Legitimate receipt must pass verification
    assert vault.verify_settlement_receipt(receipt) is True

    # Tampered receipt with altered winner payout must fail verification
    tampered_receipt = dict(receipt)
    tampered_receipt["payout_sol"] = 999.99  # Attempted balance inflation
    assert vault.verify_settlement_receipt(tampered_receipt) is False


def test_identical_wallets_prevented(wallets):
    f1, _, arbiter = wallets
    vault = DuelEscrowVault(arbiter_wallet=arbiter)

    # A duelist cannot duel themselves to manipulate fees or wash trade
    with pytest.raises(EscrowSecurityError, match="cannot be identical"):
        vault.create_match_escrow("self_duel", f1, f1, wager_sol=0.05)


def test_combat_engine_stamina_and_hp_bounds():
    f1 = GladiatorProfile(
        id="f1",
        name="Berserker",
        persona="Lore",
        class_type=GladiatorClass.CYBER_BERSERKER,
        wallet_address="11111111111111111111111111111111",
        stats=GladiatorStats(max_hp=100, hp=10, max_stamina=100, stamina=0, attack=30, defense=5)
    )
    f2 = GladiatorProfile(
        id="f2",
        name="Sentinel",
        persona="Lore",
        class_type=GladiatorClass.AEGIS_SENTINEL,
        wallet_address="22222222222222222222222222222222",
        stats=GladiatorStats(max_hp=100, hp=100, max_stamina=100, stamina=50, attack=20, defense=20)
    )

    # f1 tries to use expensive SURGE_STRIKE with 0 stamina
    m1 = MoveDecision(action=ActionType.SURGE_STRIKE, rationale="Desperate", battle_cry="Die!")
    m2 = MoveDecision(action=ActionType.HEAVY_ATTACK, rationale="Smash", battle_cry="Crush!")

    tr = CombatEngine.resolve_round(1, f1, m1, f2, m2)

    # Stamina must never drop below 0
    assert f1.stats.stamina >= 0
    # Overkill damage must clamp HP cleanly
    assert f1.stats.hp <= 0
