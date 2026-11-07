# ⚡ SolGladiator — MLH Solana Hackathon Official Submission Package

> **Event:** Solana Hackathon on MLH (Event Slug: `solana-hackathon`)  
> **Submission Deadline:** November 8, 1:00 PM EST  
> **Repository:** [https://github.com/satanic47/SolGladiator](https://github.com/satanic47/SolGladiator)  
> **Live Demo Portal:** [https://satanic47.github.io/SolGladiator/](https://satanic47.github.io/SolGladiator/)  

---

## 📋 1. Core Submission Metadata

| Field | Content |
|---|---|
| **Project Name** | **SolGladiator** |
| **Short Description (One-Line Pitch)** | Autonomous AI cyber-gladiator arena on Solana where neural combat agents clash in tactical duels backed by non-custodial PDA escrow smart vaults. |
| **Source Code URL** | `https://github.com/satanic47/SolGladiator` |
| **Live Demo Portal** | `https://satanic47.github.io/SolGladiator/` |
| **Technologies (`built_with`)** | `Solana`, `Rust`, `Anchor`, `Python`, `FastAPI`, `Ed25519`, `JavaScript`, `HTML5 Canvas`, `Web Audio API`, `CSS3` |
| **AI Tools (`ai_tools`)** | `antigravity`, `coding:google/gemini-2.5-pro` |

---

## 🎯 2. Prize Category Entries & `sponsor_usage` Answers

SolGladiator is engineered to compete in all 5 hackathon tracks:

### 🏆 Category 1: Top 3 Overall ($1,000 USD Microgrant)
- **Track Selection:** `Top 3 Overall`
- **Sponsor Usage / Pitch Answer:**
  > *"SolGladiator delivers an end-to-end production architecture: an Anchor smart contract with PDA seeds `[b'duel_escrow', match_id]`, replay-guarded double-settlement prevention, a Python FastAPI microservice with native Ed25519 cryptographic signatures, and a 60FPS cyberpunk canvas frontend featuring 4 articulated battle robot miniatures, a 10-step interactive tutorial tour, and a 100% passing automated test suite (23/23 tests)."*

### 🤖 Category 2: AI Track Top Prize ($100 USD Digital Gift Card)
- **Track Selection:** `AI Track Top Prize`
- **Sponsor Usage / Pitch Answer:**
  > *"Features 4 autonomous neural combat personas (Cyber Berserker, Aegis Sentinel, Arcane Tactician, Shadow Striker) running stamina-constrained minimax and tactical bias matrices. Each agent evaluates opponent telemetry in real time, formulates explainable thought rationale, and projects dynamic battle cries during autonomous combat."*

### 💰 Category 3: DeFi Track Top Prize ($100 USD Digital Gift Card)
- **Track Selection:** `DeFi Track Top Prize`
- **Sponsor Usage / Pitch Answer:**
  > *"Implements a non-custodial DuelEscrowVault smart vault. Both fighters' wagers are locked in a deterministic Solana Devnet PDA, verified through SHA-256 duel digest hashes, deducting a 2% protocol treasury fee and dispersing net payouts directly to the victor's wallet with sub-second finality."*

### 🎮 Category 4: Gaming Track Top Prize ($100 USD Digital Gift Card)
- **Track Selection:** `Gaming Track Top Prize`
- **Sponsor Usage / Pitch Answer:**
  > *"Built with a high-performance 60FPS HTML5 canvas rendering perspective 3D neon retro grids, articulated Real-Steel mech miniatures, procedural contact shadows, ground fissures, piercing plasma beams, hard-light honeycomb shields, and zero-dependency Web Audio API sound synthesis."*

### ⚡ Category 5: Best Beginner Hack ($100 USD Digital Gift Card)
- **Track Selection:** `Best Beginner Hack`
- **Sponsor Usage / Pitch Answer:**
  > *"Eliminates all Web3 onboarding friction for beginner players and judges via a 1-Click Guest Wallet generator that instantly mints an in-memory Ed25519 keypair and requests an airdrop on Solana Devnet, accompanied by an interactive 10-step guided tour."*

---

## 📝 3. Full Project Description (Devpost / MLH Markdown)

### 💡 Inspiration
Turn-based combat games are often plagued by opaque RNG and centralized custodial betting platforms. With Solana's sub-second settlement times and fractions-of-a-cent fees, we saw an opportunity to build **SolGladiator**: a trustless, transparent cyberpunk battle arena where players can either duel directly or stake on autonomous AI neural agents fighting on-chain.

### ⚔️ What It Does
1. **Autonomous AI Cyber-Gladiators:** 4 unique champions (Axe-01 Overclock, Titan-04 Sol Bastion, Kage-9 Neon Phantom, Vex-Null Siphon) with individual playstyles, tactical matrices, explainable neural thought streams, and custom Real-Steel miniatures.
2. **Deep Counter-Combat Mechanics:**
   - **Light Jab:** Fast low-cost attack that interrupts recharging opponents for 1.5x damage.
   - **Heavy Cleave:** High kinetic damage that can be parried into lethal counter-ripostes.
   - **Parry Shield:** Hard-light honeycomb barrier reflecting 70% damage back on heavy attacks.
   - **Arcane Burst:** Piercing singularity beam that passes straight through hard-light shields.
   - **Focus Recharge:** Restores 40 EP flux, but leaves the mech vulnerable to interrupt strikes.
3. **Non-Custodial Solana Escrow:** Mutual wagers are deposited into a Program Derived Address (`[b"duel_escrow", match_id]`), guarded by replay protection, and settled directly to the victor's address with a 2% protocol treasury burn.
4. **Zero-Friction 1-Click Guest Onboarding:** Players can mint an in-browser Ed25519 keypair and receive Devnet SOL immediately without needing browser extensions.
5. **Interactive 10-Step Guided Tour:** In-arena tutorial spotlighting the health HUD, energy flux, combat buttons, neural rationale, and Solana cryptographic ledger.

### 🛠️ How We Built It
- **Smart Contracts:** Rust & Anchor (`contracts/solgladiator_escrow.rs`) with PDA state management and reentrancy guards.
- **Backend & Cryptography:** Python 3.10 & FastAPI with native Ed25519 cryptographic keypair derivation, deterministic duel digest SHA-256 hashing, and live Solana Devnet RPC integration.
- **AI Agent Engine:** Heuristic utility trees combining stamina costs, opponent energy telemetry, class affinities, and explainable neural reasoning generation.
- **Frontend & VFX:** 60FPS pure HTML5 Canvas with perspective floor grid, realistic Real-Steel robot sprites with organic feathered contours, particle physics, screen shake, and Web Audio API synthesized cyberpunk SFX.
- **Verification:** 23 automated tests covering replay defense, unauthorized drains, tiebreakers, stamina depletion, and state machines with 100% pass rate.

### 🚧 Challenges We Ran Into
- **Replay & Double-Settlement Defense:** Ensuring that network lag or malicious duplicate calls cannot double-claim escrow funds. We solved this with monotonic slot tracking and idempotent settlement states.
- **Visual Mech Polish:** Eliminating hard rectangular sprite cuts to create high-definition, organic Real-Steel brawler miniatures with proper facing directions, breathing bob, and dynamic attack/defense/healing visuals.
- **Zero-Backend GitHub Pages Support:** Engineering client-side simulation fallbacks so the live GitHub Pages demo is 100% playable for judges without requiring local Python execution.

### 🌟 Accomplishments That We're Proud Of
- 100% test coverage across 23 security, AI, engine, and escrow unit tests.
- Sub-second round resolution and instantaneous guest wallet provisioning on Solana.
- Seamless dual-mode execution: full local Python/Rust backend or standalone in-browser demo on GitHub Pages.

### 📚 What We Learned
- Advanced PDA seed derivation and account validation patterns in Anchor.
- Building transparent, explainable tactical AI agents for turn-based Web3 games.

### 🚀 What's Next for SolGladiator
- Mainnet deployment with SPL token wagering (BONK, USDC).
- Community champion custom NFT minting and cosmetic mech chassis skins.
- Mobile PWA release with haptic feedback.
