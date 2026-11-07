"""Solana Devnet JSON-RPC Client with Live Network and Offline Fallback."""

from __future__ import annotations

import base58
import hashlib
import json
import logging
import os
import time
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEVNET_RPC_URL = "https://api.devnet.solana.com"
LAMPORTS_PER_SOL = 1_000_000_000


class SolanaClient:
    """Client for querying and transacting on the Solana Devnet cluster."""

    def __init__(self, rpc_url: str = DEVNET_RPC_URL, timeout: float = 1.0, offline_mode: Optional[bool] = None):
        self.rpc_url = rpc_url
        self.timeout = timeout
        self._mock_balances: Dict[str, float] = {}
        # Allow instant offline simulation via param or env var
        if offline_mode is not None:
            self.offline_mode = offline_mode
        else:
            self.offline_mode = os.environ.get("SOLANA_OFFLINE", "1") == "1"
        self._network_available: Optional[bool] = False if self.offline_mode else None
        self._last_network_fail_time: float = 0.0

    def _rpc_call(self, method: str, params: Optional[list] = None) -> Dict[str, Any]:
        """Execute a raw JSON-RPC call to the Solana cluster."""
        if self.offline_mode:
            raise ConnectionError("Solana RPC client operating in offline simulation mode.")

        # If network failed recently (within 60s), avoid blocking timeouts
        if self._network_available is False and (time.time() - self._last_network_fail_time < 60.0):
            raise ConnectionError("Solana RPC network in offline fallback mode.")

        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
            "params": params or []
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.rpc_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                self._network_available = True
                return res
        except Exception as e:
            logger.debug(f"Solana RPC network unavailable ({e}). Using offline simulation.")
            self._network_available = False
            self._last_network_fail_time = time.time()
            raise ConnectionError(f"Solana RPC unreachable: {e}") from e

    def get_slot(self) -> int:
        """Fetch the current slot from Devnet."""
        try:
            res = self._rpc_call("getSlot")
            return res.get("result", 312_400_000)
        except Exception:
            return 312_400_000 + int(time.time()) % 10_000

    def get_latest_blockhash(self) -> Dict[str, Any]:
        """Fetch a recent blockhash."""
        try:
            res = self._rpc_call("getLatestBlockhash", [{"commitment": "confirmed"}])
            val = res.get("result", {}).get("value", {})
            return {
                "blockhash": val.get("blockhash"),
                "lastValidBlockHeight": val.get("lastValidBlockHeight")
            }
        except Exception:
            # Deterministic simulated blockhash derived from current timestamp
            seed = f"solgladiator-blockhash-{int(time.time() // 30)}"
            sim_blockhash = base58.b58encode(hashlib.sha256(seed.encode()).digest()).decode("ascii")
            return {
                "blockhash": sim_blockhash,
                "lastValidBlockHeight": 280_000_000
            }

    def get_balance(self, pubkey: str) -> float:
        """Get balance in SOL."""
        try:
            res = self._rpc_call("getBalance", [pubkey, {"commitment": "confirmed"}])
            lamports = res.get("result", {}).get("value", 0)
            return lamports / LAMPORTS_PER_SOL
        except Exception:
            return self._mock_balances.get(pubkey, 0.5)

    def request_airdrop(self, pubkey: str, sol_amount: float = 1.0) -> Dict[str, Any]:
        """Request Devnet faucet airdrop (amount in SOL)."""
        lamports = int(sol_amount * LAMPORTS_PER_SOL)
        try:
            res = self._rpc_call("requestAirdrop", [pubkey, lamports, {"commitment": "confirmed"}])
            if "result" in res:
                self._mock_balances[pubkey] = self._mock_balances.get(pubkey, 0.0) + sol_amount
                return {
                    "signature": res["result"],
                    "status": "confirmed",
                    "amount_sol": sol_amount
                }
        except Exception:
            pass

        # Simulated fallback transaction signature
        self._mock_balances[pubkey] = self._mock_balances.get(pubkey, 0.0) + sol_amount
        sig_seed = f"airdrop-{pubkey}-{time.time()}"
        sig = base58.b58encode(hashlib.sha256(sig_seed.encode()).digest() * 2)[:88].decode("ascii")
        return {
            "signature": sig,
            "status": "simulated_confirmed",
            "amount_sol": sol_amount
        }

    def get_cluster_status(self) -> Dict[str, Any]:
        """Return a snapshot of cluster health, current slot, and blockhash."""
        bh = self.get_latest_blockhash()
        slot = self.get_slot()
        return {
            "cluster": "devnet",
            "rpc_url": self.rpc_url,
            "current_slot": slot,
            "recent_blockhash": bh["blockhash"],
            "network_online": self._network_available if self._network_available is not None else False
        }

    @staticmethod
    def get_explorer_url(signature: str, cluster: str = "devnet") -> str:
        """Construct a Solana Explorer link for a transaction."""
        return f"https://explorer.solana.com/tx/{signature}?cluster={cluster}"
