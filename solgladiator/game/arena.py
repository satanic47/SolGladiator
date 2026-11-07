"""Arena Match Orchestrator for SolGladiator.

Coordinates fighter initialization, escrow creation on Solana,
round execution, win condition verification, and instant on-chain settlement.
"""

from __future__ import annotations

import uuid
from typing import Dict, Any, Optional
from solgladiator.game.models import (
    GladiatorProfile,
    MoveDecision,
    TurnResult,
    MatchState
)
from solgladiator.game.engine import CombatEngine
from solgladiator.blockchain.wallet import SolanaWallet
from solgladiator.blockchain.escrow import DuelEscrowVault


class ArenaDuelMatch:
    """Manages an entire combat duel and its on-chain Solana escrow lifecycle."""

    def __init__(
        self,
        fighter1: GladiatorProfile,
        fighter2: GladiatorProfile,
        wager_sol: float = 0.05,
        fighter1_wallet: Optional[SolanaWallet] = None,
        fighter2_wallet: Optional[SolanaWallet] = None,
        arbiter_wallet: Optional[SolanaWallet] = None,
        escrow_vault: Optional[DuelEscrowVault] = None,
        match_id: Optional[str] = None
    ):
        self.match_id = match_id or f"match_{uuid.uuid4().hex[:12]}"
        self.fighter1 = fighter1.model_copy(deep=True)
        self.fighter2 = fighter2.model_copy(deep=True)
        self.wager_sol = wager_sol

        # Ensure we have active wallets to sign deposits consistent with profile addresses
        if fighter1_wallet:
            self.fighter1_wallet = fighter1_wallet
        else:
            self.fighter1_wallet = SolanaWallet.from_seed_phrase(f"solgladiator-seed-{self.fighter1.id}-mlh-2026")
        self.fighter1.wallet_address = self.fighter1_wallet.public_key

        if fighter2_wallet:
            self.fighter2_wallet = fighter2_wallet
        else:
            self.fighter2_wallet = SolanaWallet.from_seed_phrase(f"solgladiator-seed-{self.fighter2.id}-mlh-2026")
        self.fighter2.wallet_address = self.fighter2_wallet.public_key
        self.arbiter_wallet = arbiter_wallet or SolanaWallet.generate()
        self.vault = escrow_vault or DuelEscrowVault(arbiter_wallet=self.arbiter_wallet)

        self.current_round = 0
        self.max_rounds = 20
        self.is_game_over = False
        self.winner_id: Optional[str] = None
        self.loser_id: Optional[str] = None
        self.history: list[TurnResult] = []

        # Lock escrow deposit on Solana
        self.escrow: Dict[str, Any] = self.vault.create_match_escrow(
            match_id=self.match_id,
            fighter1_wallet=self.fighter1_wallet,
            fighter2_wallet=self.fighter2_wallet,
            wager_sol=self.wager_sol
        )
        self.settlement_receipt: Optional[Dict[str, Any]] = None

    def execute_turn(self, move1: MoveDecision, move2: MoveDecision) -> TurnResult:
        """Execute one round of combat between the fighters."""
        if self.is_game_over:
            raise ValueError(f"Match {self.match_id} is already concluded.")

        self.current_round += 1
        turn_result = CombatEngine.resolve_round(
            round_number=self.current_round,
            f1=self.fighter1,
            m1=move1,
            f2=self.fighter2,
            m2=move2
        )
        self.history.append(turn_result)

        # Check win/loss conditions
        f1_dead = self.fighter1.stats.hp <= 0
        f2_dead = self.fighter2.stats.hp <= 0

        if f1_dead and f2_dead:
            # Mutual knockout: fighter with more total stamina wins
            self.is_game_over = True
            if self.fighter1.stats.stamina >= self.fighter2.stats.stamina:
                self.winner_id = self.fighter1.id
                self.loser_id = self.fighter2.id
            else:
                self.winner_id = self.fighter2.id
                self.loser_id = self.fighter1.id
            self._finalize_and_settle()
        elif f1_dead:
            self.is_game_over = True
            self.winner_id = self.fighter2.id
            self.loser_id = self.fighter1.id
            self._finalize_and_settle()
        elif f2_dead:
            self.is_game_over = True
            self.winner_id = self.fighter1.id
            self.loser_id = self.fighter2.id
            self._finalize_and_settle()
        elif self.current_round >= self.max_rounds:
            # Round limit reached: Winner is whoever has higher HP
            self.is_game_over = True
            if self.fighter1.stats.hp >= self.fighter2.stats.hp:
                self.winner_id = self.fighter1.id
                self.loser_id = self.fighter2.id
            else:
                self.winner_id = self.fighter2.id
                self.loser_id = self.fighter1.id
            self._finalize_and_settle()

        return turn_result

    def _finalize_and_settle(self) -> None:
        """Settle match escrow on Solana Devnet to disburse rewards to the victor."""
        if not self.winner_id:
            return

        winner_pubkey = (
            self.fighter1.wallet_address
            if self.winner_id == self.fighter1.id
            else self.fighter2.wallet_address
        )

        duel_summary = {
            "match_id": self.match_id,
            "rounds_fought": self.current_round,
            "winner_id": self.winner_id,
            "loser_id": self.loser_id,
            "final_hp_f1": self.fighter1.stats.hp,
            "final_hp_f2": self.fighter2.stats.hp,
        }

        receipt = self.vault.settle_match_escrow(
            match_id=self.match_id,
            winner_pubkey=winner_pubkey,
            duel_summary=duel_summary
        )
        self.settlement_receipt = receipt

    def get_state(self) -> MatchState:
        """Return the current match state snapshot."""
        escrow_dict = dict(self.escrow)
        if self.settlement_receipt:
            escrow_dict["settlement_receipt"] = self.settlement_receipt

        return MatchState(
            match_id=self.match_id,
            fighter1=self.fighter1,
            fighter2=self.fighter2,
            current_round=self.current_round,
            max_rounds=self.max_rounds,
            is_game_over=self.is_game_over,
            winner_id=self.winner_id,
            loser_id=self.loser_id,
            history=self.history,
            escrow=escrow_dict
        )
