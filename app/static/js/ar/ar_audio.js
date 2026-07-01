/**
 * ARSounds — Efectos de sonido procedurales para actividades AR
 * Usa Web Audio API pura: sin archivos de audio, sin librerías externas.
 * Todos los métodos fallan silenciosamente si el contexto no está disponible.
 */
const ARSounds = {
  _ctx: null,

  /** Inicializar AudioContext — debe llamarse desde un evento de usuario */
  init() {
    if (this._ctx) return;
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (Ctx) this._ctx = new Ctx();
    } catch (e) {
      // Audio no disponible en este dispositivo/browser
    }
  },

  _ctx_ready() {
    if (!this._ctx) return null;
    if (this._ctx.state === 'suspended') this._ctx.resume();
    return this._ctx;
  },

  /** Explosión: ruido percusivo corto (0.18 s) */
  playExplosion() {
    const ctx = this._ctx_ready();
    if (!ctx) return;

    const dur = 0.18;
    const bufSize = Math.floor(ctx.sampleRate * dur);
    const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < bufSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / bufSize, 1.5);
    }

    const src = ctx.createBufferSource();
    src.buffer = buf;

    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 220;
    filter.Q.value = 0.6;

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.5, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);

    src.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    src.start();
  },

  /** Error: tono descendente (0.25 s) */
  playError() {
    const ctx = this._ctx_ready();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(420, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(140, ctx.currentTime + 0.22);

    gain.gain.setValueAtTime(0.22, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.25);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.26);
  },

  /** Beep de timer: ping suave al quedar pocos segundos */
  playTimerBeep() {
    const ctx = this._ctx_ready();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.value = 900;

    gain.gain.setValueAtTime(0, ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.14, ctx.currentTime + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.14);
  },

  /** Fanfare de victoria: arpegio ascendente (0.55 s) */
  playVictory() {
    const ctx = this._ctx_ready();
    if (!ctx) return;

    const notes = [523.25, 659.25, 783.99, 1046.5]; // C5 E5 G5 C6
    notes.forEach((freq, i) => {
      const osc  = ctx.createOscillator();
      const gain = ctx.createGain();
      const t    = ctx.currentTime + i * 0.11;

      osc.type = 'triangle';
      osc.frequency.value = freq;

      gain.gain.setValueAtTime(0, t);
      gain.gain.linearRampToValueAtTime(0.22, t + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.32);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t);
      osc.stop(t + 0.35);
    });
  },
};

window.ARSounds = ARSounds;
