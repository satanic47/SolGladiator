# ⚡ SolGladiator — Cyberpunk AI Gladiator Arena on Solana

[![Live Portal](https://img.shields.io/badge/Live%20Portal-GitHub%20Pages-00f5ff?style=for-the-badge&logo=github)](https://satanic47.github.io/SolGladiator/)
[![Solana Devnet](https://img.shields.io/badge/Solana-Devnet%20Verified-14f195?style=for-the-badge&logo=solana)](https://explorer.solana.com/?cluster=devnet)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Anchor Smart Contract](https://img.shields.io/badge/Anchor-Rust%20Contract-9945ff?style=for-the-badge&logo=rust)](contracts/solgladiator_escrow.rs)
[![Tests Passing](https://img.shields.io/badge/Tests-23%2F23%20Passing-brightgreen?style=for-the-badge)](tests/)

> **🌐 Live Interactive Portal:** [https://satanic47.github.io/SolGladiator/](https://satanic47.github.io/SolGladiator/)  
> **📦 GitHub Repository:** [https://github.com/satanic47/SolGladiator](https://github.com/satanic47/SolGladiator)  
> **🏆 Built for the MLH Solana Hackathon (November 6–8, 2026)**  
> **Live Hackathon Event:** [mlh.com/events/solana-hackathon](https://www.mlh.com/events/solana-hackathon)

---

## ⚔️ What is SolGladiator?

**SolGladiator** is an on-chain cyberpunk battle arena where autonomous AI gladiators clash in tactical turn-based combat, backed by non-custodial Solana Devnet escrow smart vaults. 

Players can command their own champion or watch autonomous neural AI agents wage war. Every duel locks mutual wagers into an escrow PDA (Program Derived Address), and the outcome is settled with cryptographic arbiter proofs in sub-second finality at fractions of a cent on Solana.

---

## 🎯 Targeting All 5 Hackathon Tracks in a Single Build

| Hackathon Prize Track | Target | How SolGladiator Delivers |
|---|---|---|
| **AI Track Top Prize** ($100) | Autonomous LLM / Neural Game Theory | Autonomous AI gladiators evaluate opponent HP, stamina, and combat history to calculate optimal tactical moves, articulate transparent reasoning, and shout battle cries. |
| **DeFi Track Top Prize** ($100) | Non-Custodial Escrow & Micro-Wagers | Dual-fighter escrow PDA locks deposits, deducts 2% protocol treasury fee, and settles payout directly to the victor's wallet address. |
| **Gaming Track Top Prize** ($100) | 60FPS Cyberpunk Canvas Arena | Pure HTML5 Canvas rendering perspective 3D neon floor grids, archetype particle visual effects, screen shake, audio synthesis, and combat damage callouts. |
| **Best Beginner Hack** ($100) | Zero-Friction 1-Click Guest Wallet | Instant Ed25519 guest keypair generation and automatic 2.0 SOL Devnet airdrop with direct Solana Explorer links — zero web3 friction for judges. |
| **Top 3 Overall** ($1,000 Microgrant) | Full-Stack Production Readiness | Complete Anchor smart contract, Python FastAPI backend, robust test suite (23/23 tests passing), and cyberpunk HUD frontend. |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    User["👤 Player / Judge"] -->|1-Click Guest Wallet| WalletMgr["⚡ Solana Ed25519 Wallet"]
    User -->|Choose Gladiator & Wager| FastAPIServer["🚀 FastAPI Game Server"]

    subgraph "Combat & AI Layer"
        FastAPIServer -->|Match State| ArenaOrchestrator["🏟️ ArenaDuelMatch Orchestrator"]
        ArenaOrchestrator -->|Opponent Telemetry| AIAgent["🧠 AIGladiatorAgent (Neural Biases)"]
        AIAgent -->|Move Decision + Rationale| CombatEngine["⚔️ Counter-Combat Simulator"]
        CombatEngine -->|Parry / Arcane / Crits| ArenaOrchestrator
    end

    subgraph "On-Chain Solana Layer (Devnet)"
        ArenaOrchestrator -->|Create Vault| EscrowVault["🔒 DuelEscrowVault"]
        EscrowVault -->|Lock Deposits (PDA)| SolanaAnchor["Anchor Smart Contract\n[b'duel_escrow', match_id]"]
        CombatEngine -->|Victory Condition| EscrowVault
        EscrowVault -->|Signed Settlement Proof| SolanaExplorer["🔗 Solana Devnet Explorer"]
    end

    subgraph "Interactive Cyberpunk HUD"
        ArenaOrchestrator -->|State Update| Canvas60FPS["🎮 60FPS HTML5 Canvas"]
        Canvas60FPS --> AudioSynth["🔊 Web Audio SFX Synthesizer"]
        Canvas60FPS --> TerminalDrawer["📜 Live Cryptographic Ledger"]
    end
```

---

## 🛡️ Enterprise Security Features

1. **Replay & Double-Settlement Protection:**  
   State transition from `LOCKED` to `SETTLED` is atomic and strictly enforced. Any subsequent payout attempt is rejected with `EscrowSecurityError`.
2. **Participant Whitelist Enforcement:**  
   Settlement winner public key must be one of the two registered duelists. Arbitrary or injected addresses cannot drain the vault.
3. **Cryptographic Deposit & Settlement Signatures:**  
   Both fighters sign their deposit payloads with Ed25519 keypairs. The arbiter signs the settlement proof, which can be verified by any third-party auditor.
4. **Tamper-Evident Combat Digest:**  
   The arbiter computes a SHA-256 digest of the full match telemetry (`duel_digest`) and anchors it inside the signed Solana transaction.
5. **Wager Bounds & Input Sanitization:**  
   Wagers are restricted to valid intervals `[0.001, 10.0]` SOL to prevent overflow and spam attacks.
6. **Slot Monotonicity:**  
   Enforces `settlement_slot >= deposit_slot` to guard against simulated time-travel or re-org attacks.

---

## ⚡ Combat Counter-Matrix

| Action | Cost (EP) | Counters | Countered By | Special Mechanic |
|---|---|---|---|---|
| **🗡️ Light Jab** | 15 EP | Recharge | Shields | Interrupts `Recharge` for 1.5x bonus damage |
| **💥 Heavy Swing** | 35 EP | Fatigue | Parry Shield | High raw damage; triggers fatal recoil if parried |
| **🛡️ Parry Shield** | 10 EP | Heavy Attack | Arcane Burst | Perfect Parry reflects 70% damage back to attacker |
| **🔮 Arcane Burst** | 45 EP | Parry Shield | Speed Jabs | Bypasses physical shields and armor completely |
| **⚡ Recharge** | +40 EP | Energy Deficit | Direct Attacks | Restores energy; takes 1.5x damage if struck |
| **🔥 Surge Strike** | 60 EP | Low HP Foes | High Defense | Ultimate execution strike; requires >= 60 EP |

---

## 🚀 Quickstart & Local Setup

### 1. Requirements
- Python 3.10+
- Modern Web Browser (Chrome, Firefox, Edge, Safari)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/solgladiator.git
cd solgladiator

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Automated Test Suite
```bash
python -m pytest tests/ -v
```
*(All 23 tests cover combat mechanics, AI decision heuristics, Ed25519 cryptography, escrow vault security, and API endpoints).*

### 4. Start the SolGladiator Server
```bash
python -m uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser to enter the Cyberpunk Arena HUD!

---

## 📜 Anchor Smart Contract Reference

The on-chain Anchor contract is located at `contracts/solgladiator_escrow.rs`:
- **`initialize_duel_escrow`**: Derives PDA with seed `[b"duel_escrow", match_id]`, locks wager lamports from Fighter 1 and Fighter 2.
- **`settle_duel_escrow`**: Validates arbiter authority, transfers 98% of the pot to the winner, and sends 2% to the protocol treasury vault.

---

## 🏆 MLH Solana Hackathon Submission Details

See **[SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md)** for complete project narrative, track checkboxes, challenges overcome, and judging walkthrough.
