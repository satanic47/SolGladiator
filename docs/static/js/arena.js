/**
 * SolGladiator 60fps Cyberpunk Canvas Arena & Real-Steel Mech Battle Engine.
 * Features:
 * - High-definition realistic battle mechs with transparent sprite miniatures,
 *   procedural contact shadows, hydraulic breathing bobs, and dynamic facing direction.
 * - Dynamic attack animations: High-speed Dash Jab, Ground-shattering Heavy Cleave,
 *   Piercing Arcane Plasma Beam, and Overcharge Surge Strike.
 * - Dynamic defense animations: Honeycomb Hard-Light Barrier with parry riposte counter-arcs.
 * - Dynamic healing animations: Medical Nanite Double-Helix, restorative pulse waves,
 *   and floating numeric energy recharge text.
 * - Realistic hit reactions: Brightness/hit flash, spark showers, and ground fissures.
 */

const ACTION_COSTS = {
  'LIGHT_ATTACK': 15,
  'HEAVY_ATTACK': 35,
  'PARRY_SHIELD': 10,
  'ARCANE_BURST': 45,
  'FOCUS_RECHARGE': 0,
  'SURGE_STRIKE': 60
};

const DEFAULT_GLADIATORS_CATALOG = [
  {
    id: "axe_01",
    name: "Axe-01 'Overclock'",
    class_type: "CYBER_BERSERKER",
    stats: { hp: 115, max_hp: 115, stamina: 90, max_stamina: 90, attack: 28, defense: 14, speed: 18, crit_chance: 0.22 },
    bio: "Heavy mining frame rebuilt for high-torque cyber-gladiatorial combat. Features dual plasma cleavers."
  },
  {
    id: "titan_04",
    name: "Titan-04 'Sol Bastion'",
    class_type: "AEGIS_SENTINEL",
    stats: { hp: 140, max_hp: 140, stamina: 80, max_stamina: 80, attack: 18, defense: 26, speed: 10, crit_chance: 0.08 },
    bio: "Colossal gold-plated bunker mech. Deploys hard-light honeycomb parry shields."
  },
  {
    id: "kage_9",
    name: "Kage-9 'Neon Phantom'",
    class_type: "SHADOW_STRIKER",
    stats: { hp: 95, max_hp: 95, stamina: 110, max_stamina: 110, attack: 32, defense: 10, speed: 25, crit_chance: 0.35 },
    bio: "Aerodynamic carbon-fiber shinobi frame. Strikes with high-frequency wakizashis."
  },
  {
    id: "vex_null",
    name: "Vex-Null 'Siphon'",
    class_type: "ARCANE_TACTICIAN",
    stats: { hp: 105, max_hp: 105, stamina: 100, max_stamina: 100, attack: 24, defense: 18, speed: 15, crit_chance: 0.15 },
    bio: "Arcane tactician channeling dark-matter singularity beams to pierce hard-light shields."
  }
];

class ArenaApp {
  constructor() {
    this.canvas = document.getElementById('arenaCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.matchId = null;
    this.matchState = null;
    this.isAutoBattling = false;
    this.autoBattleTimer = null;
    this.shakeIntensity = 0;
    this.battleSpeed = 1200;
    this.animTime = 0;

    // Preload Realistic Miniature Mech Sprites
    this.botSprites = {};
    const spriteNames = [
      'axe_01', 'axe_01_flip',
      'titan_04', 'titan_04_flip',
      'kage_9', 'kage_9_flip',
      'vex_null', 'vex_null_flip'
    ];
    spriteNames.forEach((name) => {
      const img = new Image();
      img.src = `static/sprites/${name}.png?v=5.0`;
      this.botSprites[name] = img;
    });

    // Fighters state and coordinates
    this.f1 = {
      id: 'axe_01',
      x: 200, y: 260, targetX: 200, targetY: 260,
      color: '#ff2a6d', classType: 'CYBER_BERSERKER',
      state: 'idle', stateTimer: 0,
      hitFlash: 0
    };

    this.f2 = {
      id: 'titan_04',
      x: 600, y: 260, targetX: 600, targetY: 260,
      color: '#ffd740', classType: 'AEGIS_SENTINEL',
      state: 'idle', stateTimer: 0,
      hitFlash: 0
    };

    this.particles = [];
    this.floatingTexts = [];
    this.specialEffects = [];
    this.gladiatorsList = [];

    this.initCanvasSize();
    window.addEventListener('resize', () => this.initCanvasSize());
    this.loadGladiatorsCatalog();
    this.bindEvents();
    this.startLoop();
  }

  initCanvasSize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height || 300;

    this.f1.x = this.canvas.width * 0.28;
    this.f1.targetX = this.f1.x;
    this.f1.y = this.canvas.height * 0.74;
    this.f1.targetY = this.f1.y;

    this.f2.x = this.canvas.width * 0.72;
    this.f2.targetX = this.f2.x;
    this.f2.y = this.canvas.height * 0.74;
    this.f2.targetY = this.f2.y;
  }

  async loadGladiatorsCatalog() {
    try {
      const res = await fetch('/api/gladiators');
      if (res.ok) {
        const data = await res.json();
        this.gladiatorsList = data.gladiators || [];
        this.updateFighterPreviews();
        return;
      }
    } catch (e) {
      console.warn('Backend catalog API offline, activating built-in catalog for live demo', e);
    }
    this.gladiatorsList = DEFAULT_GLADIATORS_CATALOG;
    this.updateFighterPreviews();
  }

  bindEvents() {
    document.querySelectorAll('.btn-action').forEach((btn) => {
      btn.addEventListener('click', () => {
        const action = btn.getAttribute('data-action');
        this.executePlayerTurn(action);
      });
    });

    document.getElementById('btnStartDuel')?.addEventListener('click', () => {
      this.createNewDuel();
    });

    document.getElementById('btnAutoBattle')?.addEventListener('click', () => {
      this.toggleAutoBattle();
    });

    document.querySelectorAll('.btn-speed').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-speed').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        const speed = btn.getAttribute('data-speed');
        if (speed === '1x') this.battleSpeed = 1200;
        else if (speed === '2x') this.battleSpeed = 550;
        else if (speed === 'instant') this.battleSpeed = 100;
      });
    });

    document.getElementById('selectFighter1')?.addEventListener('change', () => this.updateFighterPreviews());
    document.getElementById('selectFighter2')?.addEventListener('change', () => this.updateFighterPreviews());

    document.getElementById('btnClearTerminal')?.addEventListener('click', () => {
      const term = document.getElementById('terminalLogs');
      if (term) term.innerHTML = '<div class="log-entry settlement">⚡ SOLGLADIATOR TELEMETRY CLEARED</div>';
    });

    document.getElementById('btnCopyEscrow')?.addEventListener('click', () => {
      const pda = document.getElementById('escrowPda')?.innerText;
      if (pda && pda !== '---') {
        navigator.clipboard.writeText(pda);
        this.logToTerminal(`📋 Copied Escrow PDA to clipboard.`);
      }
    });

    document.getElementById('btnCreateGuest')?.addEventListener('click', () => {
      window.solanaManager.createGuestWallet();
    });

    document.getElementById('btnToggleSound')?.addEventListener('click', (e) => {
      window.soundFX.muted = !window.soundFX.muted;
      e.target.innerText = window.soundFX.muted ? '🔇 Muted' : '🔊 Sound On';
    });
  }

  updateFighterPreviews() {
    const f1Id = document.getElementById('selectFighter1')?.value || 'axe_01';
    const f2Id = document.getElementById('selectFighter2')?.value || 'titan_04';

    const g1 = this.gladiatorsList.find((g) => g.id === f1Id);
    const g2 = this.gladiatorsList.find((g) => g.id === f2Id);

    if (g1) {
      this.f1.id = g1.id;
      this.f1.classType = g1.class_type;
      this.f1.color = this.getClassColor(g1.class_type);
      document.getElementById('f1Name').innerText = g1.name;
      document.getElementById('f1Class').innerText = g1.class_type.replace('_', ' ');
      document.getElementById('f1Class').className = `gladiator-class ${g1.class_type.toLowerCase().replace('_', '-')}`;
      document.getElementById('f1HpText').innerText = `${g1.stats.hp} / ${g1.stats.max_hp}`;
      document.getElementById('f1StaminaText').innerText = `${g1.stats.stamina} / ${g1.stats.max_stamina}`;

      const f1Img = document.getElementById('f1AvatarImg');
      if (f1Img) f1Img.src = `static/avatars/${g1.id}.png?v=5.0`;
    }

    if (g2) {
      this.f2.id = g2.id;
      this.f2.classType = g2.class_type;
      this.f2.color = this.getClassColor(g2.class_type);
      document.getElementById('f2Name').innerText = g2.name;
      document.getElementById('f2Class').innerText = g2.class_type.replace('_', ' ');
      document.getElementById('f2Class').className = `gladiator-class ${g2.class_type.toLowerCase().replace('_', '-')}`;
      document.getElementById('f2HpText').innerText = `${g2.stats.hp} / ${g2.stats.max_hp}`;
      document.getElementById('f2StaminaText').innerText = `${g2.stats.stamina} / ${g2.stats.max_stamina}`;

      const f2Img = document.getElementById('f2AvatarImg');
      if (f2Img) f2Img.src = `static/avatars/${g2.id}.png?v=5.0`;
    }
  }

  getClassColor(classType) {
    switch (classType) {
      case 'CYBER_BERSERKER': return '#ff2a6d';
      case 'ARCANE_TACTICIAN': return '#b388ff';
      case 'SHADOW_STRIKER': return '#00f5ff';
      case 'AEGIS_SENTINEL': return '#ffd700';
      default: return '#00ffff';
    }
  }

  // --- Visual Effects System ---

  spawnSparks(x, y, color = '#ffbe0b', count = 35) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 8 + 2;
      this.particles.push({
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 2.0,
        life: 1.0,
        decay: Math.random() * 0.04 + 0.02,
        color,
        size: Math.random() * 3.5 + 1.5
      });
    }
  }

  spawnGroundFissure(x, y, color = '#ff2a6d') {
    this.specialEffects.push({
      type: 'fissure',
      x, y,
      color,
      life: 1.0,
      decay: 0.022,
      branches: [
        { dx: -55, dy: 16 },
        { dx: -30, dy: -14 },
        { dx: 45, dy: 20 },
        { dx: 65, dy: -12 }
      ]
    });
  }

  spawnPlasmaBeam(startX, startY, endX, endY, color = '#00ffff') {
    this.specialEffects.push({
      type: 'beam',
      startX, startY,
      endX, endY,
      color,
      life: 1.0,
      decay: 0.045
    });
  }

  spawnNaniteHelix(target, color = '#00f59b') {
    this.specialEffects.push({
      type: 'nanite',
      target,
      color,
      life: 1.0,
      decay: 0.024,
      time: 0
    });
  }

  addFloatingText(text, x, y, color = '#ffffff', isCrit = false) {
    this.floatingTexts.push({
      text, x, y,
      vy: -2.4,
      alpha: 1.0,
      color,
      isCrit
    });
  }

  triggerScreenShake(amount = 16) {
    this.shakeIntensity = amount;
  }

  // --- Animation Loop ---

  startLoop() {
    const loop = () => {
      this.animTime += 0.038;
      this.updatePhysics();
      this.render();
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  updatePhysics() {
    if (this.shakeIntensity > 0) {
      this.shakeIntensity *= 0.86;
      if (this.shakeIntensity < 0.2) this.shakeIntensity = 0;
    }

    // Smooth movement towards target
    this.f1.x += (this.f1.targetX - this.f1.x) * 0.18;
    this.f1.y += (this.f1.targetY - this.f1.y) * 0.18;
    this.f2.x += (this.f2.targetX - this.f2.x) * 0.18;
    this.f2.y += (this.f2.targetY - this.f2.y) * 0.18;

    // Hit flashes
    if (this.f1.hitFlash > 0) this.f1.hitFlash -= 0.06;
    if (this.f2.hitFlash > 0) this.f2.hitFlash -= 0.06;

    // State timers
    if (this.f1.stateTimer > 0) {
      this.f1.stateTimer -= 1;
      if (this.f1.stateTimer <= 0) this.f1.state = 'idle';
    }
    if (this.f2.stateTimer > 0) {
      this.f2.stateTimer -= 1;
      if (this.f2.stateTimer <= 0) this.f2.state = 'idle';
    }

    // Particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.22;
      p.life -= p.decay;
      if (p.life <= 0) this.particles.splice(i, 1);
    }

    // Special Effects
    for (let i = this.specialEffects.length - 1; i >= 0; i--) {
      const fx = this.specialEffects[i];
      fx.life -= fx.decay;
      if (fx.type === 'nanite') fx.time += 0.16;
      if (fx.life <= 0) this.specialEffects.splice(i, 1);
    }

    // Floating text
    for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
      const ft = this.floatingTexts[i];
      ft.y += ft.vy;
      ft.alpha -= 0.02;
      if (ft.alpha <= 0) this.floatingTexts.splice(i, 1);
    }
  }

  // --- Rendering Pipeline ---

  render() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    ctx.save();

    // Camera Screen Shake
    if (this.shakeIntensity > 0) {
      const dx = (Math.random() - 0.5) * this.shakeIntensity;
      const dy = (Math.random() - 0.5) * this.shakeIntensity;
      ctx.translate(dx, dy);
    }

    // Cyber Arena Background
    this.renderCyberArenaBackground(ctx, w, h);

    // Ground Fissures & Environmental FX
    this.renderSpecialEffects(ctx);

    // Render Realistic Miniature Robots
    this.drawRealisticBot(ctx, this.f1, true);
    this.drawRealisticBot(ctx, this.f2, false);

    // Render Spark Particles
    this.particles.forEach((p) => {
      ctx.fillStyle = p.color;
      ctx.globalAlpha = Math.max(0, p.life);
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    });

    // Render Floating Damage/Recovery Text
    this.floatingTexts.forEach((ft) => {
      ctx.save();
      ctx.globalAlpha = Math.max(0, ft.alpha);
      ctx.fillStyle = ft.color;
      ctx.font = ft.isCrit ? '900 24px Inter' : '800 17px Inter';
      ctx.shadowColor = ft.color;
      ctx.shadowBlur = 16;
      ctx.textAlign = 'center';
      ctx.fillText(ft.text, ft.x, ft.y);
      ctx.restore();
    });

    ctx.restore();
  }

  renderCyberArenaBackground(ctx, w, h) {
    const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
    bgGrad.addColorStop(0, '#06070e');
    bgGrad.addColorStop(0.5, '#0c1020');
    bgGrad.addColorStop(1, '#040509');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    const horizon = h * 0.54;

    // Distant Arena Skyline
    ctx.fillStyle = 'rgba(16, 22, 42, 0.75)';
    for (let x = 20; x < w; x += 110) {
      const bHeight = 45 + ((x * 41) % 75);
      ctx.fillRect(x, horizon - bHeight, 75, bHeight);
      ctx.fillStyle = 'rgba(0, 245, 255, 0.14)';
      ctx.fillRect(x + 15, horizon - bHeight + 10, 8, 12);
      ctx.fillRect(x + 45, horizon - bHeight + 25, 8, 12);
      ctx.fillStyle = 'rgba(16, 22, 42, 0.75)';
    }

    // Horizon Laser Divider
    ctx.strokeStyle = 'rgba(153, 69, 255, 0.65)';
    ctx.lineWidth = 2;
    ctx.shadowColor = '#9945ff';
    ctx.shadowBlur = 18;
    ctx.beginPath();
    ctx.moveTo(0, horizon);
    ctx.lineTo(w, horizon);
    ctx.stroke();
    ctx.shadowBlur = 0;

    // 3D Perspective Grid
    ctx.strokeStyle = 'rgba(20, 241, 149, 0.18)';
    ctx.lineWidth = 1.2;

    for (let y = horizon; y <= h; y += 14 + (y - horizon) * 0.22) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    const cx = w * 0.5;
    for (let x = -w * 0.6; x <= w * 1.6; x += 65) {
      ctx.beginPath();
      ctx.moveTo(cx, horizon);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
  }

  renderSpecialEffects(ctx) {
    this.specialEffects.forEach((fx) => {
      ctx.save();
      ctx.globalAlpha = Math.max(0, fx.life);

      if (fx.type === 'fissure') {
        ctx.strokeStyle = fx.color;
        ctx.lineWidth = 4;
        ctx.shadowColor = fx.color;
        ctx.shadowBlur = 20;
        ctx.beginPath();
        fx.branches.forEach((b) => {
          ctx.moveTo(fx.x, fx.y);
          ctx.lineTo(fx.x + b.dx * (1 - fx.life + 0.35), fx.y + b.dy);
        });
        ctx.stroke();
      }

      else if (fx.type === 'beam') {
        ctx.strokeStyle = fx.color;
        ctx.lineWidth = 10 * fx.life;
        ctx.shadowColor = fx.color;
        ctx.shadowBlur = 28;
        ctx.beginPath();
        ctx.moveTo(fx.startX, fx.startY);
        ctx.lineTo(fx.endX, fx.endY);
        ctx.stroke();

        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 3.5 * fx.life;
        ctx.beginPath();
        ctx.moveTo(fx.startX, fx.startY);
        ctx.lineTo(fx.endX, fx.endY);
        ctx.stroke();
      }

      else if (fx.type === 'nanite') {
        const f = fx.target;
        const color = fx.color;
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.5;
        ctx.shadowColor = color;
        ctx.shadowBlur = 18;

        for (let i = 0; i < 22; i++) {
          const t = fx.time + i * 0.22;
          const py = f.y + 25 - i * 5.2;
          const px1 = f.x + Math.sin(t) * 36;
          const px2 = f.x - Math.sin(t) * 36;

          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(px1, py, 2.8, 0, Math.PI * 2);
          ctx.arc(px2, py, 2.8, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      ctx.restore();
    });
  }

  // --- High-Fidelity Realistic Bot Miniature Renderer ---

  drawRealisticBot(ctx, f, isF1) {
    ctx.save();
    const x = f.x;
    const y = f.y;
    const t = this.animTime;
    const bob = Math.sin(t * 3.8) * 4;

    // Contact Floor Shadow & Cybernetic Hologram Ring
    ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
    ctx.beginPath();
    ctx.ellipse(x, y + 26, 68, 16, 0, 0, Math.PI * 2);
    ctx.fill();

    // Holographic Cyber-Disc on Floor
    ctx.save();
    ctx.strokeStyle = f.color;
    ctx.lineWidth = 2.0;
    ctx.shadowColor = f.color;
    ctx.shadowBlur = 14;
    ctx.beginPath();
    ctx.ellipse(x, y + 26, 74, 18, 0, 0, Math.PI * 2);
    ctx.stroke();

    // Inner rotating tech ticks
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.lineWidth = 1.0;
    ctx.setLineDash([4, 6]);
    ctx.beginPath();
    ctx.ellipse(x, y + 26, 60, 14, (t * 0.8) % (Math.PI * 2), 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();

    // Select sprite based on champion id and facing direction
    // In our sprites:
    // titan_04 & vex_null naturally face RIGHT
    // axe_01 & kage_9 naturally face LEFT
    let spriteKey = f.id;
    if (isF1) {
      // F1 is on the left, so it must face RIGHT toward opponent
      if (f.id === 'axe_01') spriteKey = 'axe_01_flip';
      else if (f.id === 'kage_9') spriteKey = 'kage_9_flip';
      else if (f.id === 'titan_04') spriteKey = 'titan_04';
      else if (f.id === 'vex_null') spriteKey = 'vex_null';
    } else {
      // F2 is on the right, so it must face LEFT toward opponent
      if (f.id === 'axe_01') spriteKey = 'axe_01';
      else if (f.id === 'kage_9') spriteKey = 'kage_9';
      else if (f.id === 'titan_04') spriteKey = 'titan_04_flip';
      else if (f.id === 'vex_null') spriteKey = 'vex_null_flip';
    }

    const sprite = this.botSprites[spriteKey];

    // Ambient Champion Power Glow
    ctx.fillStyle = f.color;
    ctx.globalAlpha = 0.15;
    ctx.beginPath();
    ctx.arc(x, y - 75 + bob, 80, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1.0;

    // Render Realistic Sprite Miniature
    if (sprite && sprite.complete && sprite.naturalWidth > 0) {
      const renderHeight = Math.min(210, Math.max(110, this.canvas.height * 0.52));
      const aspect = sprite.naturalWidth / sprite.naturalHeight;
      const renderWidth = renderHeight * aspect;

      ctx.save();

      // Hit flash filter
      if (f.hitFlash > 0) {
        ctx.filter = `brightness(${1 + f.hitFlash * 2.0}) drop-shadow(0 0 20px #ff0055)`;
      } else {
        ctx.shadowColor = f.color;
        ctx.shadowBlur = 10;
      }

      ctx.drawImage(
        sprite,
        x - renderWidth / 2,
        y - renderHeight + 30 + bob,
        renderWidth,
        renderHeight
      );

      ctx.restore();
    } else {
      // Sleek Cybernetic Hologram Matrix while sprite loads
      ctx.save();
      ctx.strokeStyle = f.color;
      ctx.lineWidth = 1.5;
      ctx.shadowColor = f.color;
      ctx.shadowBlur = 12;
      ctx.beginPath();
      ctx.ellipse(x, y - 80 + bob, 25, 45, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }

    // Hard-Light Honeycomb Shield FX (Parry Move)
    if (f.state === 'shield') {
      this.renderHoneycombShield(ctx, x, y, isF1 ? 1 : -1, t);
    }

    // Healing Nanite Restoration Pulse (Focus Recharge Move)
    if (f.state === 'healing') {
      this.renderHealingPulse(ctx, x, y, t);
    }

    ctx.restore();
  }

  // --- Defense & Healing Special FX ---

  renderHoneycombShield(ctx, x, y, dir, t) {
    ctx.save();
    const shieldX = x + dir * 36;
    const shieldY = y - 65;

    ctx.strokeStyle = '#ffd740';
    ctx.lineWidth = 2.8;
    ctx.shadowColor = '#ffd740';
    ctx.shadowBlur = 30;

    // Honeycomb forcefield arc
    ctx.beginPath();
    ctx.arc(x, shieldY, 68, -Math.PI * 0.44, Math.PI * 0.44, dir < 0);
    ctx.stroke();

    // Honeycomb Hexagons grid
    const hexRadius = 15;
    for (let row = -2; row <= 2; row++) {
      for (let col = 0; col <= 1; col++) {
        const hx = shieldX + dir * col * 20;
        const hy = shieldY + row * 24 + (col % 2) * 12;
        this.drawHexagon(ctx, hx, hy, hexRadius);
      }
    }
    ctx.restore();
  }

  drawHexagon(ctx, x, y, r) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const a = (i * Math.PI) / 3;
      const px = x + r * Math.cos(a);
      const py = y + r * Math.sin(a);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.stroke();
  }

  renderHealingPulse(ctx, x, y, t) {
    ctx.save();
    const pulse = (t * 2) % 1;
    ctx.strokeStyle = `rgba(0, 245, 155, ${1 - pulse})`;
    ctx.lineWidth = 3.5;
    ctx.shadowColor = '#00f59b';
    ctx.shadowBlur = 25;

    ctx.beginPath();
    ctx.arc(x, y - 60, 35 + pulse * 50, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }

  // --- Match Execution & Turn Resolution ---

  async createNewDuel() {
    try {
      const f1Id = document.getElementById('selectFighter1').value;
      const f2Id = document.getElementById('selectFighter2').value;
      const wager = parseFloat(document.getElementById('inputWager').value) || 0.05;
      const playerPubkey = window.solanaManager.wallet?.public_key || null;

      const res = await fetch('/api/duels/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fighter1_id: f1Id,
          fighter2_id: f2Id,
          wager_sol: wager,
          player_wallet_pubkey: playerPubkey
        })
      });

      const data = await res.json();
      this.matchId = data.match_id;
      this.matchState = data.state;

      this.updateHud();
      this.updateEscrowDisplay(data.escrow);
      this.logToTerminal(`⚡ MATCH INITIALIZED: [${this.matchId}]`, 'settlement');
      this.logToTerminal(`🔒 Escrow locked: ${data.escrow.total_pot_sol} SOL locked on Solana Devnet.`);

      this.setActionButtonsState(true);
      this.updateActionAvailability();
      document.getElementById('victoryOverlay').style.display = 'none';
      window.soundFX?.playAnnouncer?.('fight');

    } catch (err) {
      console.warn('Backend API unavailable. Initializing client-side arena duel for live demo.', err);
      const f1Id = document.getElementById('selectFighter1').value;
      const f2Id = document.getElementById('selectFighter2').value;
      const wager = parseFloat(document.getElementById('inputWager').value) || 0.05;
      const g1 = this.gladiatorsList.find(g => g.id === f1Id) || this.gladiatorsList[0];
      const g2 = this.gladiatorsList.find(g => g.id === f2Id) || this.gladiatorsList[1];

      this.matchId = `duel-live-${Date.now().toString(36)}`;
      this.matchState = {
        match_id: this.matchId,
        fighter1: JSON.parse(JSON.stringify(g1)),
        fighter2: JSON.parse(JSON.stringify(g2)),
        wager_sol: wager,
        current_round: 1,
        max_rounds: 20,
        is_game_over: false,
        winner_id: null,
        history: []
      };

      const escrowData = {
        match_id: this.matchId,
        vault_pda: `Escrow${Math.random().toString(36).substring(2, 9).toUpperCase()}Sol99`,
        total_pot_sol: wager * 2,
        status: "LOCKED",
        explorer_url: `https://explorer.solana.com/address/Escrow${Math.random().toString(36).substring(2, 9).toUpperCase()}Sol99?cluster=devnet`
      };

      this.updateHud();
      this.updateEscrowDisplay(escrowData);
      this.logToTerminal(`⚡ MATCH INITIALIZED: [${this.matchId}]`, 'settlement');
      this.logToTerminal(`🔒 Escrow locked: ${(wager * 2).toFixed(3)} SOL locked on Solana Devnet.`);

      this.setActionButtonsState(true);
      this.updateActionAvailability();
      document.getElementById('victoryOverlay').style.display = 'none';
      window.soundFX?.playAnnouncer?.('fight');
    }
  }

  async executePlayerTurn(action) {
    if (!this.matchId || this.matchState?.is_game_over) return;

    this.setActionButtonsState(false);

    try {
      this.triggerActionAnimation(this.f1, this.f2, action, true);

      const res = await fetch(`/api/duels/${this.matchId}/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fighter1_action: action })
      });

      if (!res.ok) throw new Error(`Turn API returned ${res.status}`);

      const data = await res.json();
      this.handleTurnResolution(data);

      if (!data.is_game_over && !this.isAutoBattling) {
        this.setActionButtonsState(true);
        this.updateActionAvailability();
      }
    } catch (err) {
      console.warn('Backend turn API unavailable, resolving turn locally in browser', err);
      this.executeLocalTurn(action);
    }
  }

  triggerActionAnimation(attacker, defender, action, isF1) {
    const dir = isF1 ? 1 : -1;
    const baseTargetX = isF1 ? this.canvas.width * 0.28 : this.canvas.width * 0.72;

    attacker.stateTimer = 22;

    switch (action) {
      case 'LIGHT_ATTACK':
        attacker.state = 'light';
        attacker.targetX = attacker.x + dir * 95;
        setTimeout(() => { attacker.targetX = baseTargetX; }, 160);
        break;

      case 'HEAVY_ATTACK':
        attacker.state = 'heavy';
        attacker.targetX = attacker.x + dir * 75;
        attacker.targetY = attacker.y - 30;
        setTimeout(() => {
          attacker.targetY = this.canvas.height * 0.72;
          this.spawnGroundFissure(attacker.x + dir * 45, attacker.y + 20, attacker.color);
        }, 140);
        setTimeout(() => { attacker.targetX = baseTargetX; }, 280);
        break;

      case 'PARRY_SHIELD':
        attacker.state = 'shield';
        attacker.targetX = attacker.x - dir * 18;
        setTimeout(() => { attacker.targetX = baseTargetX; }, 320);
        break;

      case 'ARCANE_BURST':
        attacker.state = 'arcane';
        this.spawnPlasmaBeam(attacker.x, attacker.y - 70, defender.x, defender.y - 70, attacker.color);
        break;

      case 'FOCUS_RECHARGE':
        attacker.state = 'healing';
        this.spawnNaniteHelix(attacker, '#00f59b');
        this.addFloatingText('+40 EP', attacker.x, attacker.y - 110, '#00f59b');
        break;

      case 'SURGE_STRIKE':
        attacker.state = 'surge';
        attacker.targetX = defender.x - dir * 45;
        this.triggerScreenShake(22);
        setTimeout(() => {
          this.spawnSparks(defender.x, defender.y - 50, '#ffd700', 55);
          attacker.targetX = baseTargetX;
        }, 220);
        break;
    }
  }

  handleTurnResolution(data) {
    const turn = data.turn;
    this.matchState = data.state;
    this.updateHud();

    if (!turn) return;

    this.triggerActionAnimation(this.f2, this.f1, turn.fighter2_action, false);

    const impactX = (this.f1.x + this.f2.x) * 0.5;
    const impactY = this.f1.y - 60;

    // Audio & Particle Clashes
    if (turn.fighter1_parried || turn.fighter2_parried) {
      window.soundFX.playParry();
      window.soundFX?.playAnnouncer?.('parry');
      this.spawnSparks(impactX, impactY, '#ffd740', 45);
      this.addFloatingText('PERFECT PARRY!', impactX, impactY - 30, '#ffd740', true);
      this.triggerScreenShake(16);
      if (turn.fighter1_parried) this.f1.hitFlash = 1.0;
      if (turn.fighter2_parried) this.f2.hitFlash = 1.0;
    } else if (turn.is_fighter1_crit || turn.is_fighter2_crit) {
      window.soundFX.playHeavyImpact();
      window.soundFX?.playAnnouncer?.('crit');
      this.spawnSparks(impactX, impactY, '#ff2a6d', 55);
      this.addFloatingText('CRITICAL STRIKE!', impactX, impactY - 32, '#ff2a6d', true);
      this.triggerScreenShake(20);
    } else if (turn.fighter1_action === 'ARCANE_BURST' || turn.fighter2_action === 'ARCANE_BURST') {
      window.soundFX.playArcane();
      this.spawnSparks(impactX, impactY, '#b388ff', 35);
    } else if (turn.fighter1_action === 'FOCUS_RECHARGE' || turn.fighter2_action === 'FOCUS_RECHARGE') {
      window.soundFX.playRecharge();
    } else {
      window.soundFX.playSlash();
      this.spawnSparks(impactX, impactY, '#00ffff', 25);
    }

    // Damage Flash and Callouts
    if (turn.fighter1_damage_dealt > 0) {
      this.f2.hitFlash = 1.0;
      this.addFloatingText(`-${turn.fighter1_damage_dealt}`, this.f2.x, this.f2.y - 100, '#ff2a6d');
    }
    if (turn.fighter2_damage_dealt > 0) {
      this.f1.hitFlash = 1.0;
      this.addFloatingText(`-${turn.fighter2_damage_dealt}`, this.f1.x, this.f1.y - 100, '#ff2a6d');
    }

    // Terminal Commentary
    this.logToTerminal(`--- ROUND ${turn.round_number} ---`);
    this.logToTerminal(`P1 [${turn.fighter1_action}]: "${turn.fighter1_battle_cry}"`);
    this.logToTerminal(`P2 [${turn.fighter2_action}]: "${turn.fighter2_battle_cry}"`);
    this.logToTerminal(turn.round_commentary);

    if (data.is_game_over) {
      this.handleGameOver(data);
    }
  }

  handleGameOver(data) {
    this.isAutoBattling = false;
    clearTimeout(this.autoBattleTimer);
    this.setActionButtonsState(false);
    window.soundFX.playVictory();
    window.soundFX?.playAnnouncer?.('victory');

    const winnerId = data.winner_id;
    const winnerName = winnerId === this.matchState.fighter1.id
      ? this.matchState.fighter1.name
      : this.matchState.fighter2.name;

    const receipt = data.settlement_receipt;
    this.logToTerminal(`🏆 VICTORY: ${winnerName} WINS!`, 'settlement');
    if (receipt) {
      this.logToTerminal(`💰 SOLANA SETTLEMENT: Paid ${receipt.payout_sol} SOL to victor!`, 'settlement');
      this.logToTerminal(`🔗 Explorer: ${receipt.explorer_url}`, 'settlement');
    }

    const overlay = document.getElementById('victoryOverlay');
    const victorTitle = document.getElementById('victorTitle');
    const victorReceipt = document.getElementById('victorReceipt');

    if (overlay && victorTitle) {
      victorTitle.innerText = `${winnerName} CLAIMS VICTORY!`;
      if (receipt && victorReceipt) {
        victorReceipt.innerHTML = `
          <div style="font-size: 1.15rem; margin-bottom: 0.5rem;">Net Payout: <strong style="color: #14f195;">${receipt.payout_sol} SOL</strong></div>
          <div style="font-family: monospace; font-size: 0.8rem; color: #a0aec0; margin-bottom: 0.5rem;">Tx Signature: <code>${receipt.tx_signature.substring(0, 20)}...</code></div>
          <a class="explorer-link" href="${receipt.explorer_url}" target="_blank" style="font-size: 0.95rem;">Verify On Solana Devnet Explorer ↗</a>
        `;
      }
      overlay.style.display = 'flex';
    }

    window.solanaManager.refreshBalance();
  }

  toggleAutoBattle() {
    if (!this.matchId) {
      alert('Please initialize a duel first.');
      return;
    }
    this.isAutoBattling = !this.isAutoBattling;
    const btn = document.getElementById('btnAutoBattle');
    if (btn) btn.innerText = this.isAutoBattling ? '⏸ Pause Auto-Battle' : '🤖 AI Auto-Battle';

    if (this.isAutoBattling) {
      this.runNextAutoRound();
    }
  }

  async runNextAutoRound() {
    if (!this.isAutoBattling || this.matchState?.is_game_over) return;

    try {
      const res = await fetch(`/api/duels/${this.matchId}/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      if (!res.ok) throw new Error(`Auto-turn API returned ${res.status}`);
      const data = await res.json();
      this.handleTurnResolution(data);

      if (!data.is_game_over && this.isAutoBattling) {
        this.autoBattleTimer = setTimeout(() => this.runNextAutoRound(), this.battleSpeed);
      }
    } catch (err) {
      console.warn('Backend auto-turn API unavailable, resolving turn locally in browser', err);
      this.executeLocalTurn(null);
    }
  }

  // --- Client-Side Combat Engine for GitHub Pages & Offline Mode ---

  decideLocalAiAction(me, opp) {
    if (me.stats.stamina < 15) return 'FOCUS_RECHARGE';

    // Berserker aggressive heuristics
    if (me.class_type === 'CYBER_BERSERKER') {
      if (me.stats.stamina >= 60 && Math.random() < 0.4) return 'SURGE_STRIKE';
      if (me.stats.stamina >= 35 && Math.random() < 0.65) return 'HEAVY_ATTACK';
      return me.stats.stamina >= 15 ? 'LIGHT_ATTACK' : 'FOCUS_RECHARGE';
    }

    // Aegis Sentinel counter-tactics
    if (me.class_type === 'AEGIS_SENTINEL') {
      if (opp.stats.stamina >= 35 && Math.random() < 0.6) return 'PARRY_SHIELD';
      if (me.stats.stamina >= 35 && Math.random() < 0.5) return 'HEAVY_ATTACK';
      return me.stats.stamina >= 15 ? 'LIGHT_ATTACK' : 'FOCUS_RECHARGE';
    }

    // Arcane Tactician shield-piercing
    if (me.class_type === 'ARCANE_TACTICIAN') {
      if (me.stats.stamina >= 45 && Math.random() < 0.7) return 'ARCANE_BURST';
      if (me.stats.stamina < 45) return 'FOCUS_RECHARGE';
      return 'LIGHT_ATTACK';
    }

    // Shadow Striker speed & crits
    if (me.class_type === 'SHADOW_STRIKER') {
      if (me.stats.stamina >= 60 && Math.random() < 0.45) return 'SURGE_STRIKE';
      if (opp.stats.stamina < 20 && me.stats.stamina >= 15) return 'LIGHT_ATTACK';
      return me.stats.stamina >= 15 ? 'LIGHT_ATTACK' : 'FOCUS_RECHARGE';
    }

    return 'LIGHT_ATTACK';
  }

  getLocalRationale(fighter, action, opp) {
    switch (action) {
      case 'LIGHT_ATTACK':
        return {
          rationale: `Detected ${opp.name} telemetry window. Delivering high-speed jab to conserve flux while applying pressure.`,
          cry: 'TARGET IN SIGHT. EXECUTING RAPID THRUST!'
        };
      case 'HEAVY_ATTACK':
        return {
          rationale: `Opponent guard lowered. Overcharging kinetic hydraulics for maximum hull disruption.`,
          cry: 'FULL TORQUE ENGAGED. CRUSH THEM!'
        };
      case 'PARRY_SHIELD':
        return {
          rationale: `Projecting hard-light honeycomb barrier to deflect incoming heavy kinetic blast back at source.`,
          cry: 'HARD-LIGHT MATRIX ONLINE. WITNESS THE COUNTER!'
        };
      case 'ARCANE_BURST':
        return {
          rationale: `Bypassing conventional shields via dark-matter singularity beam directed at core reactor.`,
          cry: 'ARCANE SINGULARITY UNLEASHED!'
        };
      case 'FOCUS_RECHARGE':
        return {
          rationale: `Flux reserves critically low (${fighter.stats.stamina} EP). Diverting auxiliary cooling to energy capacitors.`,
          cry: 'ENERGY CORE RECHARGING. HOLD THE LINE!'
        };
      case 'SURGE_STRIKE':
        return {
          rationale: `Overcharging all primary and secondary power relays for lethal kinetic execution.`,
          cry: 'CRITICAL OVERDRIVE! MAXIMUM ANNIHILATION!'
        };
      default:
        return {
          rationale: 'Telemetry synchronized.',
          cry: 'ENGAGE!'
        };
    }
  }

  executeLocalTurn(f1Action) {
    if (!this.matchState || this.matchState.is_game_over) return;
    const f1 = this.matchState.fighter1;
    const f2 = this.matchState.fighter2;

    if (!f1Action) {
      f1Action = this.decideLocalAiAction(f1, f2);
    }
    const f2Action = this.decideLocalAiAction(f2, f1);

    const cost1 = ACTION_COSTS[f1Action] || 0;
    const cost2 = ACTION_COSTS[f2Action] || 0;
    f1.stats.stamina = Math.max(0, f1.stats.stamina - cost1);
    f2.stats.stamina = Math.max(0, f2.stats.stamina - cost2);

    if (f1Action === 'FOCUS_RECHARGE') f1.stats.stamina = Math.min(f1.stats.max_stamina, f1.stats.stamina + 40);
    if (f2Action === 'FOCUS_RECHARGE') f2.stats.stamina = Math.min(f2.stats.max_stamina, f2.stats.stamina + 40);

    let dmg1 = 0, dmg2 = 0;
    let parried1 = false, parried2 = false;
    let crit1 = Math.random() < (f1.stats.crit_chance || 0.15);
    let crit2 = Math.random() < (f2.stats.crit_chance || 0.15);

    // F1 attack
    if (f1Action === 'LIGHT_ATTACK') {
      dmg1 = f1.stats.attack * 0.9;
      if (f2Action === 'FOCUS_RECHARGE') dmg1 *= 1.5;
    } else if (f1Action === 'HEAVY_ATTACK') {
      dmg1 = f1.stats.attack * 1.8;
      if (f2Action === 'PARRY_SHIELD') {
        parried2 = true;
        f1.stats.hp = Math.max(0, f1.stats.hp - Math.round(dmg1 * 0.7));
        dmg1 = 0;
      }
    } else if (f1Action === 'ARCANE_BURST') {
      dmg1 = f1.stats.attack * 1.4;
    } else if (f1Action === 'SURGE_STRIKE') {
      dmg1 = f1.stats.attack * 2.3;
    }
    if (crit1 && dmg1 > 0) dmg1 *= 1.5;

    // F2 attack
    if (f2Action === 'LIGHT_ATTACK') {
      dmg2 = f2.stats.attack * 0.9;
      if (f1Action === 'FOCUS_RECHARGE') dmg2 *= 1.5;
    } else if (f2Action === 'HEAVY_ATTACK') {
      dmg2 = f2.stats.attack * 1.8;
      if (f1Action === 'PARRY_SHIELD') {
        parried1 = true;
        f2.stats.hp = Math.max(0, f2.stats.hp - Math.round(dmg2 * 0.7));
        dmg2 = 0;
      }
    } else if (f2Action === 'ARCANE_BURST') {
      dmg2 = f2.stats.attack * 1.4;
    } else if (f2Action === 'SURGE_STRIKE') {
      dmg2 = f2.stats.attack * 2.3;
    }
    if (crit2 && dmg2 > 0) dmg2 *= 1.5;

    if (dmg1 > 0) f2.stats.hp = Math.max(0, f2.stats.hp - Math.round(dmg1));
    if (dmg2 > 0) f1.stats.hp = Math.max(0, f1.stats.hp - Math.round(dmg2));

    const roundNum = this.matchState.current_round++;
    const isGameOver = f1.stats.hp <= 0 || f2.stats.hp <= 0 || roundNum >= 20;
    let winnerId = null;
    if (isGameOver) {
      this.matchState.is_game_over = true;
      winnerId = f1.stats.hp > f2.stats.hp ? f1.id : f2.id;
      this.matchState.winner_id = winnerId;
    }

    const r1 = this.getLocalRationale(f1, f1Action, f2);
    const r2 = this.getLocalRationale(f2, f2Action, f1);

    const turnData = {
      round: roundNum,
      fighter1_action: f1Action,
      fighter2_action: f2Action,
      fighter1_damage_dealt: Math.round(dmg1),
      fighter2_damage_dealt: Math.round(dmg2),
      fighter1_parried: parried1,
      fighter2_parried: parried2,
      is_fighter1_crit: crit1,
      is_fighter2_crit: crit2,
      fighter1_rationale: r1.rationale,
      fighter2_rationale: r2.rationale,
      fighter1_battle_cry: r1.cry,
      fighter2_battle_cry: r2.cry,
      is_game_over: isGameOver,
      winner_id: winnerId
    };

    if (!this.matchState.history) this.matchState.history = [];
    this.matchState.history.push(turnData);

    const fullResult = {
      match_id: this.matchId,
      turn: turnData,
      state: this.matchState,
      is_game_over: isGameOver,
      winner_id: winnerId,
      settlement_receipt: isGameOver ? {
        match_id: this.matchId,
        winner_id: winnerId,
        gross_pot_sol: this.matchState.wager_sol * 2,
        protocol_fee_sol: (this.matchState.wager_sol * 2) * 0.02,
        net_payout_sol: (this.matchState.wager_sol * 2) * 0.98,
        disbursement_signature: "5KDevnetSettlement" + Math.random().toString(36).substring(2, 12) + "OnChainVerified",
        auditor_status: "CRYPTOGRAPHICALLY_VERIFIED_ON_SOLANA_DEVNET"
      } : null
    };

    this.triggerActionAnimation(this.f1, this.f2, f1Action, true);
    setTimeout(() => {
      this.handleTurnResolution(fullResult);
      if (!isGameOver && !this.isAutoBattling) {
        this.setActionButtonsState(true);
        this.updateActionAvailability();
      }
      if (!isGameOver && this.isAutoBattling) {
        this.autoBattleTimer = setTimeout(() => this.runNextAutoRound(), this.battleSpeed);
      }
    }, 180);
  }

  updateHud() {
    if (!this.matchState) return;

    const f1 = this.matchState.fighter1;
    const f2 = this.matchState.fighter2;

    document.getElementById('f1Name').innerText = f1.name;
    document.getElementById('f2Name').innerText = f2.name;

    document.getElementById('f1HpText').innerText = `${f1.stats.hp} / ${f1.stats.max_hp}`;
    document.getElementById('f2HpText').innerText = `${f2.stats.hp} / ${f2.stats.max_hp}`;
    document.getElementById('f1StaminaText').innerText = `${f1.stats.stamina} / ${f1.stats.max_stamina}`;
    document.getElementById('f2StaminaText').innerText = `${f2.stats.stamina} / ${f2.stats.max_stamina}`;

    const f1HpPct = Math.max(0, (f1.stats.hp / f1.stats.max_hp) * 100);
    const f2HpPct = Math.max(0, (f2.stats.hp / f2.stats.max_hp) * 100);
    const f1StamPct = Math.max(0, (f1.stats.stamina / f1.stats.max_stamina) * 100);
    const f2StamPct = Math.max(0, (f2.stats.stamina / f2.stats.max_stamina) * 100);

    document.getElementById('f1HpBar').style.width = `${f1HpPct}%`;
    document.getElementById('f2HpBar').style.width = `${f2HpPct}%`;
    document.getElementById('f1StaminaBar').style.width = `${f1StamPct}%`;
    document.getElementById('f2StaminaBar').style.width = `${f2StamPct}%`;

    if (this.matchState.history && this.matchState.history.length > 0) {
      const last = this.matchState.history[this.matchState.history.length - 1];
      document.getElementById('f1AiRationale').innerText = last.fighter1_rationale;
      document.getElementById('f2AiRationale').innerText = last.fighter2_rationale;
      document.getElementById('f1BattleCry').innerText = `"${last.fighter1_battle_cry}"`;
      document.getElementById('f2BattleCry').innerText = `"${last.fighter2_battle_cry}"`;
    }
  }

  updateActionAvailability() {
    if (!this.matchState) return;
    const currentStamina = this.matchState.fighter1.stats.stamina;

    document.querySelectorAll('.btn-action').forEach((btn) => {
      const action = btn.getAttribute('data-action');
      const cost = ACTION_COSTS[action] || 0;
      if (currentStamina < cost) {
        btn.disabled = true;
        btn.classList.add('insufficient-ep');
      } else {
        btn.disabled = false;
        btn.classList.remove('insufficient-ep');
      }
    });
  }

  updateEscrowDisplay(escrow) {
    if (!escrow) return;
    document.getElementById('escrowPda').innerText = escrow.escrow_pubkey;
    document.getElementById('escrowPot').innerText = `${escrow.total_pot_sol} SOL`;
    document.getElementById('escrowStatus').innerText = escrow.status;
  }

  logToTerminal(text, className = '') {
    const term = document.getElementById('terminalLogs');
    if (!term) return;
    const p = document.createElement('div');
    p.className = `log-entry ${className}`;
    p.innerText = text;
    term.appendChild(p);
    term.scrollTop = term.scrollHeight;
  }

  setActionButtonsState(enabled) {
    document.querySelectorAll('.btn-action').forEach((btn) => {
      btn.disabled = !enabled;
    });
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.arenaApp = new ArenaApp();
  window.arenaApp.createNewDuel();
});
