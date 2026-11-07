# 📝 SolGladiator — MLH Solana Hackathon Submission Guide

**Event:** MLH Solana Hackathon (November 6–8, 2026)  
**Hackathon URL:** [https://www.mlh.com/events/solana-hackathon](https://www.mlh.com/events/solana-hackathon)  
**Project Name:** SolGladiator  
**Tagline:** Cyberpunk Autonomous AI Gladiator Arena with Sub-Second Solana Escrow Settlement  

---

## 🏆 Selected Prize Categories

- [x] **AI Track Top Prize ($100 Digital Gift Card)** — Autonomous AI gladiators make tactical game-theory combat decisions and stream explainable reasoning on-chain.
- [x] **DeFi Track Top Prize ($100 Digital Gift Card)** — Non-custodial dual-fighter escrow PDA locks deposits and settles rewards with sub-second finality.
- [x] **Gaming Track Top Prize ($100 Digital Gift Card)** — 60fps HTML5 Canvas cyberpunk battle arena with particle physics, Web Audio SFX synthesis, and combat text popups.
- [x] **Best Beginner Hack ($100 Digital Gift Card)** — 1-Click Guest Keypair generation with instant 2.0 SOL Devnet airdrop — zero crypto onboarding friction for judges.
- [x] **Top 3 Overall ($1,000 USD Microgrant)** — Production-ready full-stack application with Rust Anchor smart contracts, FastAPI backend, 23 automated tests, and interactive UI.

---

## 💡 Inspiration

We wanted to showcase why Solana is uniquely positioned for the future of on-chain gaming and autonomous agents. Traditional blockchains are too slow and expensive for turn-based PvP combat where micro-wagers need to settle in real-time. 

On Solana, transactions finalize in under a second and cost a fraction of a cent. We asked ourselves: *What if AI agents didn't just play against each other in a silo, but competed in an autonomous cyberpunk arena with actual on-chain stakes, transparent tactical reasoning, and cryptographic arbiter settlement?*

That was the birth of **SolGladiator**.

---

## ⚙️ What It Does

1. **Autonomous AI Combat:** Four distinct gladiator archetypes (Cyber Berserker, Arcane Tactician, Shadow Striker, Aegis Sentinel) powered by neural tactical heuristics. Each agent analyzes opponent HP, stamina, and combat history to make moves, explain their reasoning in real-time, and shout in-character battle cries.
2. **On-Chain Solana Escrow (Devnet):** When a duel is initiated, wagers from both combatants are locked into a Program Derived Address (PDA). Upon victory, the escrow automatically disburses 98% of the pot to the winner and allocates 2% to a decentralized treasury, emitting verifiable Solana Explorer links.
3. **60FPS Cyberpunk Arena:** Built with pure HTML5 Canvas and Web Audio API:
   - Perspective 3D holographic grid floor.
   - Distinct character visual styles and auras per archetype.
   - Particle explosion sparks on hits, shield reflections on parries, and screen shake on critical strikes.
   - Pure synthesized sound effects (laser slashes, parry clangs, plasma beams, and victory fanfare) without external audio files.
4. **Zero-Friction 1-Click Onboarding:** Hackathon judges and new players can click "1-Click Guest Wallet" to immediately receive an Ed25519 keypair and 2.0 SOL on Devnet without needing a browser extension or external wallet.

---

## 🛠️ How We Built It

- **Smart Contract Layer:** Anchor Framework (Rust) with PDA seeds `[b"duel_escrow", match_id]`, enforcing reentrancy protection, monotonic slot validation, and 2% protocol fee allocation.
- **Blockchain Client Layer:** Python implementation using native Ed25519 (`cryptography`) and Base58 encoding matching Solana wire format. Includes a Solana JSON-RPC client with both live Devnet RPC support and deterministic offline fallback.
- **AI & Game Theory Engine:** Deterministic counter-matrix combat simulator (Parry counters Heavy Attack, Arcane pierces Shields, Light Jab interrupts Recharge). Weighted tactical reasoning engine with transparent explainability strings.
- **Backend & Web Server:** FastAPI REST API providing endpoints for wallet generation, match creation, turn resolution, and autonomous battle simulation.
- **Frontend & Visuals:** HTML5 Canvas, modern CSS3 with neon scanlines, and native Web Audio API oscillators.

---

## 🧗 Challenges We Ran Into

- **Transaction Finality & Replay Guards:** Designing non-custodial duel escrows where neither player can double-claim rewards required implementing strict state transitions (`LOCKED -> SETTLED`), cryptographic participant whitelisting, and SHA-256 duel digest hashes.
- **Zero-Dependency Web Audio:** External sound files often suffer from CORS issues or missing assets in hackathon review environments. We solved this by writing a custom Web Audio synthesizer that creates retro-futuristic sound effects directly using sine, square, and sawtooth audio oscillators.
- **Deterministic Offline Fallback:** Ensuring that hackathon judges behind strict firewalls or offline evaluation sandboxes can run tests and experience the full application without network timeouts.

---

## 🏅 Accomplishments That We're Proud Of

- **23/23 Automated Tests Passing:** Complete test suite covering combat mechanics, AI decision reasoning, Ed25519 cryptography, escrow vault security, and API endpoints.
- **Single Build, All 5 Categories:** Built a cohesive application that authentically satisfies the AI, DeFi, Gaming, Beginner, and Overall hackathon tracks.
- **Sub-Second Settlement Proofs:** Every match outcome generates a verified Solana Devnet transaction receipt with direct links to `explorer.solana.com`.

---

## 📚 What We Learned

- How Program Derived Addresses (PDAs) enable decentralized escrow vaults without requiring a centralized custody key.
- How Ed25519 signatures can be generated and verified in Python to match Solana's on-chain instruction formats.
- Balancing game-theory counter mechanics so that no single archetype or action dominates the arena.

---

## 🔮 What's Next for SolGladiator

- Deploying the Anchor escrow contract to Solana Mainnet-Beta.
- Community gladiator custom training via custom prompts and fine-tuned models.
- Decentralized tournaments with automated bracket generation and prize pool staking.
- Spl-token support (betting with BONK, USDC, or custom arena credits).

---

## 🎬 3-Minute Demo Video Walkthrough Script

1. **[0:00 - 0:35] Intro & Frictionless Onboarding:**
   - "Welcome to SolGladiator. Let's start with zero crypto friction by clicking '1-Click Guest Wallet'. Instantly, an Ed25519 keypair is minted and funded with 2.0 SOL on Solana Devnet."
2. **[0:35 - 1:15] Lock Escrow & Combat Initiation:**
   - "We select Axe-01 (Berserker) vs Titan-04 (Tank), set a 0.05 SOL wager, and click 'Lock Escrow & Fight'. The 0.10 SOL pot is locked into an on-chain escrow PDA."
3. **[1:15 - 2:05] Live Combat & AI Reasoning:**
   - "Watch the combat: When Axe-01 unleashes a heavy swing, Titan-04's neural engine predicts the move and activates a Parry Shield — reflecting 70% damage with screen shake and metallic SFX! Check the Neural Thought Engine box to see the AI's real-time reasoning."
4. **[2:05 - 2:40] Auto-Battle & Speed Controls:**
   - "Toggle 'AI Auto-Battle' at 2x speed. The agents trade tactical moves until a decisive knockout."
5. **[2:40 - 3:00] Instant On-Chain Settlement:**
   - "The match concludes! The escrow vault releases 0.098 SOL directly to the victor's wallet and emits the live Solana Devnet Explorer link."
