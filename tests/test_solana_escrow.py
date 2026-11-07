"""Unit Tests for Solana Ed25519 Wallets and Escrow Vault Operations."""

import pytest
from solgladiator.blockchain.wallet import SolanaWallet
from solgladiator.blockchain.escrow import DuelEscrowVault
from solgladiator.blockchain.client import SolanaClient


def test_wallet_generation_and_signatures():
    w = SolanaWallet.generate()

    assert len(w.public_key) >= 32
    assert len(w.secret_key_base58) >= 64

    message = b"SOLGLADIATOR_VERIFIED_SIGNATURE"
    sig = w.sign_base58(message)
    assert len(sig) > 40

    is_valid = SolanaWallet.verify_signature(w.public_key, message, sig)
    assert is_valid is True

    # Tampered message must fail verification
    is_tampered_valid = SolanaWallet.verify_signature(w.public_key, b"TAMPERED_DATA", sig)
    assert is_tampered_valid is False


def test_escrow_deposit_locking_and_settlement():
    f1_wallet = SolanaWallet.generate()
    f2_wallet = SolanaWallet.generate()
    arbiter = SolanaWallet.generate()

    vault = DuelEscrowVault(arbiter_wallet=arbiter)
    match_id = "test_match_999"

    # 1. Create match escrow with 0.1 SOL wager each (0.2 SOL total pot)
    escrow = vault.create_match_escrow(
        match_id=match_id,
        fighter1_wallet=f1_wallet,
        fighter2_wallet=f2_wallet,
        wager_sol=0.1
    )

    assert escrow["status"] == "LOCKED"
    assert escrow["total_pot_sol"] == 0.2
    assert escrow["fighter1_deposit_sig"] is not None
    assert escrow["fighter2_deposit_sig"] is not None

    # 2. Settle match
    receipt = vault.settle_match_escrow(
        match_id=match_id,
        winner_pubkey=f1_wallet.public_key,
        duel_summary={"winner": "f1", "rounds": 4}
    )

    assert receipt["winner"] == f1_wallet.public_key
    assert receipt["total_pot_sol"] == 0.2
    # 2% protocol fee on 0.2 SOL = 0.004 SOL; Payout = 0.196 SOL
    assert receipt["protocol_fee_sol"] == 0.004
    assert receipt["payout_sol"] == 0.196
    assert receipt["tx_signature"] is not None
    assert "https://explorer.solana.com/tx/" in receipt["explorer_url"]
    assert "cluster=devnet" in receipt["explorer_url"]
