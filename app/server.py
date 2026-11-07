"""SolGladiator FastAPI Web Server and REST API.

Provides endpoints for guest wallet onboarding, gladiator selection,
duel creation, turn execution, autonomous match simulation, and live Solana escrow settlement.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add parent directory to sys.path so solgladiator is discoverable
APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from solgladiator.blockchain.wallet import SolanaWallet
from solgladiator.blockchain.client import SolanaClient, LAMPORTS_PER_SOL
from solgladiator.ai.personas import GLADIATOR_PERSONAS, create_default_gladiators
from solgladiator.ai.agent import AIGladiatorAgent
from solgladiator.game.models import (
    ActionType,
    GladiatorClass,
    GladiatorProfile,
    MoveDecision,
    TurnResult,
    MatchState,
)
from solgladiator.game.arena import ArenaDuelMatch
from solgladiator.game.engine import STAMINA_COSTS

app = FastAPI(
    title="SolGladiator API",
    description="Cyberpunk AI Autonomous Gladiator Arena with On-Chain Solana Escrow",
    version="1.0.0"
)

# Enable CORS for local and web previews
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active matches
ACTIVE_MATCHES: Dict[str, ArenaDuelMatch] = {}
AI_AGENTS: Dict[str, Dict[str, AIGladiatorAgent]] = {}
SOLANA_CLIENT = SolanaClient()
DEFAULT_GLADIATORS = create_default_gladiators()


# ---------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------

class CreateMatchRequest(BaseModel):
    fighter1_id: str = Field(default="axe_01", description="ID of fighter 1 (e.g. axe_01, vex_null)")
    fighter2_id: str = Field(default="titan_04", description="ID of fighter 2 (e.g. kage_9, titan_04)")
    wager_sol: float = Field(default=0.05, ge=0.001, le=10.0, description="Wager amount per fighter in SOL")
    player_wallet_pubkey: Optional[str] = Field(default=None, description="Optional custom Solana wallet public key")


class ExecuteTurnRequest(BaseModel):
    fighter1_action: Optional[ActionType] = Field(default=None, description="Player 1 chosen action (if human)")
    fighter2_action: Optional[ActionType] = Field(default=None, description="Player 2 chosen action (if human)")


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    """System health check and Solana Devnet network status."""
    slot = SOLANA_CLIENT.get_slot()
    blockhash_info = SOLANA_CLIENT.get_latest_blockhash()
    return {
        "status": "online",
        "game": "SolGladiator",
        "solana_cluster": "devnet",
        "current_slot": slot,
        "blockhash": blockhash_info["blockhash"],
        "active_matches": len(ACTIVE_MATCHES)
    }


@app.get("/api/gladiators")
def list_gladiators() -> Dict[str, Any]:
    """Retrieve all available gladiator champions, lore, stats, and addresses."""
    output = []
    for gid, profile in DEFAULT_GLADIATORS.items():
        meta = GLADIATOR_PERSONAS.get(gid, {})
        output.append({
            "id": profile.id,
            "name": profile.name,
            "lore": profile.persona,
            "class_type": profile.class_type.value,
            "wallet_address": profile.wallet_address,
            "stats": profile.stats.model_dump(),
            "avatar_url": profile.avatar_url,
            "tactical_biases": {k.value: v for k, v in meta.get("tactical_biases", {}).items()},
            "taunts": meta.get("taunts", [])
        })
    return {"gladiators": output}


@app.post("/api/wallet/guest")
def generate_guest_wallet() -> Dict[str, Any]:
    """
    Generate an instant Ed25519 guest wallet on Solana Devnet.
    Provides 0-friction onboarding for hackathon judges (Best Beginner Hack Track).
    """
    wallet = SolanaWallet.generate()
    # Request devnet airdrop (or simulated devnet airdrop)
    airdrop_res = SOLANA_CLIENT.request_airdrop(wallet.public_key, sol_amount=2.0)
    balance_sol = SOLANA_CLIENT.get_balance(wallet.public_key)

    return {
        "public_key": wallet.public_key,
        "secret_key_base58": wallet.secret_key_base58,
        "balance_sol": balance_sol,
        "airdrop_status": airdrop_res.get("status"),
        "airdrop_signature": airdrop_res.get("signature"),
        "cluster": "devnet",
        "explorer_url": f"https://explorer.solana.com/address/{wallet.public_key}?cluster=devnet"
    }


@app.get("/api/wallet/{pubkey}/balance")
def get_wallet_balance(pubkey: str) -> Dict[str, Any]:
    """Check live SOL balance on Solana Devnet."""
    balance = SOLANA_CLIENT.get_balance(pubkey)
    return {
        "public_key": pubkey,
        "balance_sol": balance,
        "explorer_url": f"https://explorer.solana.com/address/{pubkey}?cluster=devnet"
    }


@app.post("/api/duels/create")
def create_duel(req: CreateMatchRequest) -> Dict[str, Any]:
    """Create a new arena duel and lock wagers into an on-chain Solana escrow."""
    f1_template = DEFAULT_GLADIATORS.get(req.fighter1_id)
    f2_template = DEFAULT_GLADIATORS.get(req.fighter2_id)

    if not f1_template or not f2_template:
        raise HTTPException(status_code=400, detail="Invalid fighter ID specified.")

    f1 = f1_template.model_copy(deep=True)
    f2 = f2_template.model_copy(deep=True)

    if req.player_wallet_pubkey:
        f1.wallet_address = req.player_wallet_pubkey

    match = ArenaDuelMatch(
        fighter1=f1,
        fighter2=f2,
        wager_sol=req.wager_sol
    )

    ACTIVE_MATCHES[match.match_id] = match
    AI_AGENTS[match.match_id] = {
        f1.id: AIGladiatorAgent(match.fighter1),
        f2.id: AIGladiatorAgent(match.fighter2)
    }

    return {
        "match_id": match.match_id,
        "state": match.get_state().model_dump(),
        "escrow": match.escrow
    }


@app.get("/api/duels/{match_id}")
def get_duel_status(match_id: str) -> Dict[str, Any]:
    """Retrieve the current state of a duel."""
    match = ACTIVE_MATCHES.get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Duel not found.")
    return match.get_state().model_dump()


@app.post("/api/duels/{match_id}/turn")
def execute_turn(match_id: str, req: ExecuteTurnRequest) -> Dict[str, Any]:
    """
    Execute one round of combat.
    If action is omitted for either fighter, their AI agent decides the move.
    """
    match = ACTIVE_MATCHES.get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Duel not found.")

    if match.is_game_over:
        return {
            "is_game_over": True,
            "winner_id": match.winner_id,
            "settlement_receipt": match.settlement_receipt,
            "state": match.get_state().model_dump()
        }

    agents = AI_AGENTS.get(match_id, {})
    agent1 = agents.get(match.fighter1.id)
    agent2 = agents.get(match.fighter2.id)

    # Resolve Fighter 1 Decision
    if req.fighter1_action:
        cost1 = STAMINA_COSTS.get(req.fighter1_action, 15)
        m1 = MoveDecision(
            action=req.fighter1_action,
            rationale=f"Human commander commanded {req.fighter1_action.value}.",
            battle_cry="Locked and loaded!",
            stamina_cost=cost1
        )
    else:
        m1 = agent1.decide_move(match.fighter2, match.history, match.current_round)

    # Resolve Fighter 2 Decision
    if req.fighter2_action:
        cost2 = STAMINA_COSTS.get(req.fighter2_action, 15)
        m2 = MoveDecision(
            action=req.fighter2_action,
            rationale=f"Human commander commanded {req.fighter2_action.value}.",
            battle_cry="Brace yourself!",
            stamina_cost=cost2
        )
    else:
        m2 = agent2.decide_move(match.fighter1, match.history, match.current_round)

    turn_result = match.execute_turn(m1, m2)

    return {
        "turn": turn_result.model_dump(),
        "state": match.get_state().model_dump(),
        "is_game_over": match.is_game_over,
        "winner_id": match.winner_id,
        "settlement_receipt": match.settlement_receipt
    }


@app.post("/api/duels/{match_id}/simulate")
def simulate_full_duel(match_id: str) -> Dict[str, Any]:
    """
    Run an automated battle until conclusion between AI agents and settle on Solana.
    """
    match = ACTIVE_MATCHES.get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Duel not found.")

    agents = AI_AGENTS.get(match_id, {})
    agent1 = agents.get(match.fighter1.id)
    agent2 = agents.get(match.fighter2.id)

    rounds_executed = []
    while not match.is_game_over:
        m1 = agent1.decide_move(match.fighter2, match.history, match.current_round)
        m2 = agent2.decide_move(match.fighter1, match.history, match.current_round)
        tr = match.execute_turn(m1, m2)
        rounds_executed.append(tr.model_dump())

    return {
        "match_id": match_id,
        "rounds_executed": rounds_executed,
        "total_rounds": match.current_round,
        "winner_id": match.winner_id,
        "settlement_receipt": match.settlement_receipt,
        "state": match.get_state().model_dump()
    }


# ---------------------------------------------------------
# Static File Mounting & Web UI
# ---------------------------------------------------------

static_path = APP_DIR / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
def root():
    """Serve the Cyberpunk Arena HUD Frontend."""
    index_file = static_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(
        content={"message": "SolGladiator API is running. UI not found at /static/index.html"},
        status_code=200
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("solgladiator.app.server:app", host="0.0.0.0", port=8000, reload=True)
