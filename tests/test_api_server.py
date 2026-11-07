"""Integration and Contract Tests for SolGladiator API Endpoints."""

import pytest
from app.server import (
    health_check,
    list_gladiators,
    generate_guest_wallet,
    get_wallet_balance,
    create_duel,
    get_duel_status,
    execute_turn,
    simulate_full_duel,
    CreateMatchRequest,
    ExecuteTurnRequest
)
from solgladiator.game.models import ActionType


def test_health_check_endpoint():
    data = health_check()
    assert data["status"] == "online"
    assert data["game"] == "SolGladiator"
    assert data["solana_cluster"] == "devnet"
    assert "current_slot" in data


def test_gladiators_listing():
    data = list_gladiators()
    glads = data["gladiators"]
    assert len(glads) >= 4
    ids = [g["id"] for g in glads]
    assert "axe_01" in ids
    assert "titan_04" in ids
    assert "vex_null" in ids
    assert "kage_9" in ids


def test_guest_wallet_onboarding():
    data = generate_guest_wallet()
    assert "public_key" in data
    assert len(data["public_key"]) >= 32
    assert data["balance_sol"] >= 2.0
    assert "explorer_url" in data
    assert "cluster=devnet" in data["explorer_url"]


def test_duel_lifecycle_create_and_turn():
    # 1. Create Duel
    req = CreateMatchRequest(fighter1_id="axe_01", fighter2_id="titan_04", wager_sol=0.05)
    match_data = create_duel(req)

    match_id = match_data["match_id"]
    assert match_id is not None
    assert match_data["escrow"]["total_pot_sol"] == 0.1
    assert match_data["escrow"]["status"] == "LOCKED"

    # 2. Query status
    status = get_duel_status(match_id)
    assert status["match_id"] == match_id
    assert status["current_round"] == 0

    # 3. Execute a Turn with explicit human action
    turn_req = ExecuteTurnRequest(fighter1_action=ActionType.LIGHT_ATTACK)
    turn_data = execute_turn(match_id, turn_req)

    assert turn_data["turn"]["round_number"] == 1
    assert "state" in turn_data
    assert turn_data["state"]["current_round"] == 1


def test_duel_simulation_and_settlement():
    # 1. Create Duel
    req = CreateMatchRequest(fighter1_id="vex_null", fighter2_id="kage_9", wager_sol=0.05)
    match_data = create_duel(req)
    match_id = match_data["match_id"]

    # 2. Simulate until victory
    sim_data = simulate_full_duel(match_id)

    assert sim_data["winner_id"] in ["vex_null", "kage_9"]
    assert sim_data["total_rounds"] >= 1
    assert sim_data["settlement_receipt"] is not None
    assert "tx_signature" in sim_data["settlement_receipt"]
    assert "explorer_url" in sim_data["settlement_receipt"]
    assert sim_data["settlement_receipt"]["payout_sol"] == 0.098
