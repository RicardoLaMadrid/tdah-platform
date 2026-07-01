/**
 * ARActivity — Motor base para actividades de espacio 3D inmersivo.
 * Reemplaza el paradigma "magic window" con cámara por un entorno espacial completo.
 * Las actividades existentes (caza, secuencia, respiracion, trail_making) usan
 * su propio JS standalone y NO instancian esta clase.
 */
class ARActivity {
  constructor(config) {
    this.activityId    = config.activityId;
    this.studentId     = config.studentId;
    this.duration      = config.duration || 60;
    this.onStart       = config.onStart  || (() => {});
    this.onEnd         = config.onEnd    || (() => {});

    this.score         = 0;
    this.errors        = 0;
    this.startTime     = null;
    this.timerInterval = null;
    this.isRunning     = false;
    this.reactionTimes = [];

    this.initSpaceEnvironment();
    this._bindUI();
  }

  initSpaceEnvironment() {
    const scene = document.querySelector('a-scene');
    if (!scene) return;

    const setup = () => {
      if (!window.ARVisuals || document.getElementById('space-skybox')) return;
      try {
        if (typeof ARVisuals.buildSpaceEnvironment === 'function') {
          ARVisuals.buildSpaceEnvironment(scene);
        } else {
          ARVisuals.createSpaceSkybox(scene);
          ARVisuals.setupLighting(scene);
        }
      } catch (e) {
        console.error('Error inicializando entorno espacial:', e);
      }
    };

    if (scene.hasLoaded) setup();
    else scene.addEventListener('loaded', setup, { once: true });
  }

  _initSpace() { this.initSpaceEnvironment(); }

  _bindUI() {
    const startBtn = document.getElementById('ar-start-btn');
    const exitBtn  = document.getElementById('ar-exit-btn');
    if (startBtn) startBtn.addEventListener('click', () => this.start());
    if (exitBtn)  exitBtn.addEventListener('click',  () => this.exit());
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    this.startTime = Date.now();
    this.score  = 0;
    this.errors = 0;
    this.reactionTimes = [];

    const instructions = document.getElementById('ar-instructions');
    const hud          = document.getElementById('ar-hud');
    if (instructions) instructions.style.display = 'none';
    if (hud)          hud.style.display          = 'flex';

    this._startTimer();
    this.onStart();
  }

  _startTimer() {
    let remaining = this.duration;
    this._updateTimer(remaining);

    this.timerInterval = setInterval(() => {
      remaining--;
      this._updateTimer(remaining);
      if (remaining <= 0) this.end();
    }, 1000);
  }

  _updateTimer(seconds) {
    const el = document.getElementById('ar-timer');
    if (el) el.textContent = `${seconds}s`;
  }

  recordReactionTime(stimulusTime) {
    if (stimulusTime) this.reactionTimes.push(Date.now() - stimulusTime);
  }

  addScore(points = 1) {
    this.score += points;
    const el = document.getElementById('ar-score');
    if (el) el.textContent = this.score;
  }

  addError() {
    this.errors += 1;
    const el = document.getElementById('ar-extra-value');
    if (el) el.textContent = this.errors;
  }

  setExtraStat(label, icon, value) {
    const stat    = document.getElementById('ar-extra-stat');
    const labelEl = document.getElementById('ar-extra-label');
    const iconEl  = document.getElementById('ar-extra-icon');
    const valueEl = document.getElementById('ar-extra-value');

    if (stat)    stat.style.display = 'flex';
    if (labelEl) labelEl.textContent = label;
    if (iconEl)  iconEl.textContent  = icon;
    if (valueEl) valueEl.textContent = value;
  }

  end() {
    if (!this.isRunning) return;
    this.isRunning = false;
    clearInterval(this.timerInterval);

    const hud     = document.getElementById('ar-hud');
    const results = document.getElementById('ar-results');
    const final   = document.getElementById('ar-final-score');

    if (hud)     hud.style.display     = 'none';
    if (results) results.style.display = 'flex';
    if (final)   final.textContent     = this.score;

    const completionTime = Math.round((Date.now() - this.startTime) / 1000);
    const accuracy       = this._calculateAccuracy();
    const avgRT          = this._calculateAvgReactionTime();

    this._saveResult({ completion_time: completionTime, accuracy, avg_reaction_time: avgRT });
    this.onEnd(this.score, completionTime, accuracy);
  }

  calculateAccuracy() { return this._calculateAccuracy(); }

  _calculateAccuracy() {
    const total = this.score + this.errors;
    if (total === 0) return 100;
    return Math.round((this.score / total) * 100);
  }

  _calculateAvgReactionTime() {
    if (this.reactionTimes.length === 0) return 0;
    return Math.round(this.reactionTimes.reduce((a, b) => a + b, 0) / this.reactionTimes.length);
  }

  _calculateAttentionScore(accuracy, avgRT) {
    const accScore   = accuracy;
    const speedScore = avgRT > 0 ? Math.max(0, 100 - avgRT / 30) : 50;
    return Math.round(accScore * 0.7 + speedScore * 0.3);
  }

  async _saveResult(metrics) {
    try {
      await fetch('/ar/save-result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          activity_type: this.activityId,
          results: {
            score:           this.score,
            total_time:      metrics.completion_time,
            errors:          this.errors,
            accuracy:        metrics.accuracy,
            avg_reaction_time: metrics.avg_reaction_time,
            attention_score: this._calculateAttentionScore(
              metrics.accuracy, metrics.avg_reaction_time
            ),
            completed: true,
          },
        }),
      });
    } catch (err) {
      console.error('Error guardando resultado AR:', err);
    }
  }

  exit() {
    this.cleanup();
    window.location.href = '/ar/';
  }

  cleanup() {
    if (this.timerInterval) clearInterval(this.timerInterval);
  }

  showError(message) {
    const el = document.getElementById('ar-error');
    if (el) { el.textContent = message; el.style.display = 'block'; }
  }
}

window.addEventListener('beforeunload', () => {
  if (window.currentARActivity) window.currentARActivity.cleanup();
});
