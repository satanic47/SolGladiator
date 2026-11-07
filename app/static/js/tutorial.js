/**
 * SolGladiator Interactive 10-Step In-Website Navigation Tutorial.
 * Highlights target UI elements with neon focus rings, positions the tour tile,
 * and provides clear text, pro-tips, progress indicators, Next, Back, and Skip Tour buttons.
 */

class ArenaTutorial {
  constructor() {
    this.currentStep = 0;
    this.steps = [
      {
        target: '#btnCreateGuest',
        title: '⚡ 1-Click Guest Wallet (Best Beginner Hack)',
        desc: 'Welcome to SolGladiator! Experience zero-friction Web3 onboarding. Click this button to instantly generate an Ed25519 Solana keypair and receive an automated 2.0 SOL airdrop on Solana Devnet — no browser extensions or seed phrases required!',
        tip: 'Judges and players can start playing and betting immediately.'
      },
      {
        target: '.wallet-display',
        title: '👛 Devnet Wallet & Balance Monitor',
        desc: 'Here you can monitor your active public address and live Devnet SOL balance. Whenever an escrow deposit locks or a victory prize settles, your balance updates in real-time. Click "Explorer ↗" anytime to verify your account directly on the official Solana Explorer.',
        tip: 'Clicking the guest address copies it directly to your clipboard.'
      },
      {
        target: '.fighter-hud.f1-card',
        title: '🛡️ Challenger HUD & Archetypes',
        desc: 'Each combatant is configured with a distinct class archetype: Cyber Berserker (high attack/crit), Arcane Tactician (shield-piercing magic), Shadow Striker (high agility & speed), or Aegis Sentinel (heavy parry counter). Track Hull Integrity (HP) and Energy Flux (EP) here.',
        tip: 'Stamina management is key — running out of EP leaves you fatigued and vulnerable!'
      },
      {
        target: '.ai-reasoning-box',
        title: '🧠 Neural Thought Engine (AI Track)',
        desc: 'SolGladiator features fully explainable autonomous AI agents. The Neural Thought Engine evaluates opponent telemetry, energy reserves, and combat history in real-time. Watch the AI articulate its strategic rationale and battle cries before executing moves on-chain!',
        tip: 'Agents actively predict when their opponent is fatigued to punish them.'
      },
      {
        target: '.canvas-wrapper',
        title: '🎮 60FPS Cyberpunk Canvas Arena (Gaming Track)',
        desc: 'Watch high-stakes combat come to life on our hardware-accelerated HTML5 Canvas. Experience 3D perspective cyber grid floors, dynamic attack lunges, hard-light hexagonal shields, plasma beam auras, particle explosion sparks, and screen shake on critical hits!',
        tip: 'Our built-in Web Audio engine synthesizes arcade sound effects on the fly.'
      },
      {
        target: '.action-buttons-grid',
        title: '⚔️ Tactical Action Deck & Counters',
        desc: 'Command your gladiator using 6 specialized actions with tactical counter mechanics:\n• Light Jab (15 EP): Quick hit; interrupts Recharge for 1.5x damage!\n• Heavy Swing (35 EP): Massive crushing strike; can be parried!\n• Parry Shield (10 EP): Reflects 70% damage back on Heavy Swings!\n• Arcane Burst (45 EP): Bypasses and penetrates shields completely!\n• Recharge (+40 EP): Restores capacitor energy; vulnerable while charging!\n• Surge Strike (60 EP): Decimating ultimate finisher on low HP foes!',
        tip: 'Buttons automatically dim and lock when you don\'t have enough EP.'
      },
      {
        target: '.match-meta-bar',
        title: '⚖️ Match Config & Dual-Fighter Wagers',
        desc: 'Select any matchup from our gladiator roster and enter your duel wager in SOL (e.g., 0.05 SOL). When you click "Lock Escrow & Fight", both players\' wagers are cryptographically locked into an on-chain smart vault.',
        tip: 'Wagers are strictly bounded between 0.001 SOL and 10.0 SOL for security.'
      },
      {
        target: '.speed-controls',
        title: '🤖 AI Auto-Battle & Speed Control',
        desc: 'Want to sit back and observe autonomous AI gladiators face off? Toggle "AI Auto-Battle" to let both agents trade blows until victory. Switch speeds dynamically between 1x (tactical pace), 2x (fast), and Instant for lightning-speed benchmark simulations.',
        tip: 'You can pause and take over manual control at any point during a fight.'
      },
      {
        target: '.escrow-vault-card',
        title: '🔒 On-Chain Escrow Smart Vault (DeFi Track)',
        desc: 'Built on Solana with Anchor Program Derived Addresses (PDAs). Funds are secured with enterprise-grade protection: replay attack prevention, participant whitelisting, monotonic slot verification, and a 2% protocol fee routed to a decentralized treasury.',
        tip: 'Click "Copy PDA" to inspect the smart escrow account on Solana.'
      },
      {
        target: '#terminalLogs',
        title: '📜 Live Cryptographic Ledger & Settlement',
        desc: 'Every combat exchange, damage number, and battle cry is logged in this live terminal. Upon knockout, the arbiter computes a SHA-256 duel digest and signs a settlement transaction, paying the victor instantly with a verifiable Solana Explorer link!',
        tip: 'You\'ve completed the tutorial! Click "Finish Tour" to jump into the arena!'
      }
    ];

    this.cardEl = null;
    this.backdropEl = null;
    this.activeHighlight = null;
  }

  init() {
    this.createDomElements();
    this.bindEvents();

    // Check if user has seen the tutorial before; if not, show it automatically after 800ms
    const seen = localStorage.getItem('solgladiator_tour_completed');
    if (!seen) {
      setTimeout(() => this.startTour(0), 800);
    }
  }

  createDomElements() {
    // Backdrop overlay
    this.backdropEl = document.createElement('div');
    this.backdropEl.className = 'tour-backdrop';
    this.backdropEl.style.display = 'none';
    document.body.appendChild(this.backdropEl);

    // Tour Card
    this.cardEl = document.createElement('div');
    this.cardEl.className = 'tour-card';
    this.cardEl.style.display = 'none';
    this.cardEl.innerHTML = `
      <div class="tour-header">
        <span class="tour-badge" id="tourBadge">Step 1 of 10</span>
        <button class="tour-close-btn" id="tourBtnClose" title="Exit Tour">&times;</button>
      </div>
      <div class="tour-content">
        <h3 class="tour-title" id="tourTitle">Tour Title</h3>
        <p class="tour-desc" id="tourDesc">Tour description</p>
        <div class="tour-tip" id="tourTip">
          <span class="tip-label">💡 PRO TIP:</span>
          <span id="tourTipText"></span>
        </div>
      </div>
      <div class="tour-footer">
        <div class="tour-dots" id="tourDots"></div>
        <div class="tour-actions">
          <button class="tour-btn tour-btn-secondary" id="tourBtnSkip">Skip Tour</button>
          <button class="tour-btn tour-btn-secondary" id="tourBtnBack">Back</button>
          <button class="tour-btn tour-btn-primary" id="tourBtnNext">Next</button>
        </div>
      </div>
    `;
    document.body.appendChild(this.cardEl);

    // Render dot indicators
    const dotsContainer = this.cardEl.querySelector('#tourDots');
    dotsContainer.innerHTML = '';
    this.steps.forEach((_, idx) => {
      const dot = document.createElement('span');
      dot.className = 'tour-dot' + (idx === 0 ? ' active' : '');
      dot.title = `Step ${idx + 1}`;
      dot.addEventListener('click', () => this.goToStep(idx));
      dotsContainer.appendChild(dot);
    });
  }

  bindEvents() {
    this.cardEl.querySelector('#tourBtnClose')?.addEventListener('click', () => this.endTour());
    this.cardEl.querySelector('#tourBtnSkip')?.addEventListener('click', () => this.endTour());
    this.cardEl.querySelector('#tourBtnBack')?.addEventListener('click', () => this.prevStep());
    this.cardEl.querySelector('#tourBtnNext')?.addEventListener('click', () => this.nextStep());
    this.backdropEl?.addEventListener('click', () => this.endTour());

    // Connect header guide button
    document.getElementById('btnStartTour')?.addEventListener('click', () => {
      this.startTour(0);
    });

    // Keyboard navigation (Arrow keys + Esc)
    window.addEventListener('keydown', (e) => {
      if (this.cardEl.style.display === 'none') return;
      if (e.key === 'ArrowRight' || e.key === 'Enter') {
        this.nextStep();
      } else if (e.key === 'ArrowLeft') {
        this.prevStep();
      } else if (e.key === 'Escape') {
        this.endTour();
      }
    });

    // Reposition on window resize
    window.addEventListener('resize', () => {
      if (this.cardEl.style.display !== 'none') {
        this.positionCard(this.steps[this.currentStep].target);
      }
    });
  }

  startTour(startIndex = 0) {
    this.currentStep = startIndex;
    this.backdropEl.style.display = 'block';
    this.cardEl.style.display = 'flex';
    this.showStep(this.currentStep);
  }

  endTour() {
    this.backdropEl.style.display = 'none';
    this.cardEl.style.display = 'none';
    if (this.activeHighlight) {
      this.activeHighlight.classList.remove('tour-highlight-active');
      this.activeHighlight = null;
    }
    localStorage.setItem('solgladiator_tour_completed', 'true');
  }

  nextStep() {
    if (this.currentStep < this.steps.length - 1) {
      this.showStep(this.currentStep + 1);
    } else {
      this.endTour();
      window.arenaApp?.logToTerminal('🎉 TUTORIAL COMPLETED: You are ready for arena combat!', 'settlement');
    }
  }

  prevStep() {
    if (this.currentStep > 0) {
      this.showStep(this.currentStep - 1);
    }
  }

  goToStep(index) {
    if (index >= 0 && index < this.steps.length) {
      this.showStep(index);
    }
  }

  showStep(index) {
    this.currentStep = index;
    const step = this.steps[index];

    // Remove previous highlight
    if (this.activeHighlight) {
      this.activeHighlight.classList.remove('tour-highlight-active');
      this.activeHighlight = null;
    }

    // Update Text Content
    this.cardEl.querySelector('#tourBadge').innerText = `Step ${index + 1} of ${this.steps.length}`;
    this.cardEl.querySelector('#tourTitle').innerText = step.title;
    this.cardEl.querySelector('#tourDesc').innerHTML = step.desc.replace(/\n/g, '<br>');

    const tipEl = this.cardEl.querySelector('#tourTip');
    const tipTextEl = this.cardEl.querySelector('#tourTipText');
    if (step.tip) {
      tipTextEl.innerText = step.tip;
      tipEl.style.display = 'flex';
    } else {
      tipEl.style.display = 'none';
    }

    // Update Dots
    const dots = this.cardEl.querySelectorAll('.tour-dot');
    dots.forEach((dot, idx) => {
      dot.className = 'tour-dot' + (idx === index ? ' active' : '');
    });

    // Update Button Labels
    const backBtn = this.cardEl.querySelector('#tourBtnBack');
    const nextBtn = this.cardEl.querySelector('#tourBtnNext');
    backBtn.disabled = index === 0;

    if (index === this.steps.length - 1) {
      nextBtn.innerText = 'Finish Tour 🎉';
      nextBtn.className = 'tour-btn tour-btn-finish';
    } else {
      nextBtn.innerText = 'Next →';
      nextBtn.className = 'tour-btn tour-btn-primary';
    }

    // Highlight target element & position card
    this.highlightAndPosition(step.target);
  }

  highlightAndPosition(targetSelector) {
    const el = document.querySelector(targetSelector);
    if (!el) {
      // Fallback: center in screen
      this.cardEl.style.top = '50%';
      this.cardEl.style.left = '50%';
      this.cardEl.style.transform = 'translate(-50%, -50%)';
      return;
    }

    this.activeHighlight = el;
    el.classList.add('tour-highlight-active');
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });

    this.positionCard(targetSelector);
  }

  positionCard(targetSelector) {
    const el = document.querySelector(targetSelector);
    if (!el) return;

    const rect = el.getBoundingClientRect();
    const cardWidth = 440;
    const cardHeight = this.cardEl.offsetHeight || 300;
    const margin = 16;

    let top = 0;
    let left = 0;

    // Prefer positioning below the element
    if (rect.bottom + cardHeight + margin < window.innerHeight) {
      top = rect.bottom + margin;
      left = Math.max(margin, Math.min(window.innerWidth - cardWidth - margin, rect.left + (rect.width - cardWidth) / 2));
    }
    // Else position above the element
    else if (rect.top - cardHeight - margin > 0) {
      top = rect.top - cardHeight - margin;
      left = Math.max(margin, Math.min(window.innerWidth - cardWidth - margin, rect.left + (rect.width - cardWidth) / 2));
    }
    // Else position to the side or center
    else {
      top = Math.max(margin, Math.min(window.innerHeight - cardHeight - margin, (window.innerHeight - cardHeight) / 2));
      if (rect.right + cardWidth + margin < window.innerWidth) {
        left = rect.right + margin;
      } else if (rect.left - cardWidth - margin > 0) {
        left = rect.left - cardWidth - margin;
      } else {
        left = Math.max(margin, (window.innerWidth - cardWidth) / 2);
      }
    }

    this.cardEl.style.position = 'fixed';
    this.cardEl.style.top = `${top}px`;
    this.cardEl.style.left = `${left}px`;
    this.cardEl.style.transform = 'none';
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.arenaTutorial = new ArenaTutorial();
  window.arenaTutorial.init();
});
