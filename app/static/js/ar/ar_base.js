/**
 * ARActivity — motor base para actividades magic window AR
 * Cámara web como fondo + objetos 3D A-Frame encima, sin marcadores.
 */
class ARActivity {
  constructor(config) {
    this.activityId  = config.activityId;
    this.studentId   = config.studentId;
    this.duration    = config.duration || 60;
    this.onStart     = config.onStart  || (() => {});
    this.onEnd       = config.onEnd    || (() => {});

    this.score       = 0;
    this.startTime   = null;
    this.timerInterval = null;
    this.cameraStream  = null;
    this.isRunning   = false;

    this._initCamera();
    this._bindUI();
  }

  async _initCamera() {
    try {
      this.cameraStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 1280, height: 720 },
        audio: false
      });
      const video = document.getElementById('ar-camera-bg');
      if (video) video.srcObject = this.cameraStream;
    } catch (err) {
      this._showError('No se pudo activar la cámara: ' + err.message);
    }
  }

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
    this.score = 0;

    document.getElementById('ar-instructions').style.display = 'none';
    document.getElementById('ar-hud').style.display = 'flex';

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

  addScore(points) {
    this.score += (points || 1);
    const el = document.getElementById('ar-score');
    if (el) el.textContent = this.score;
  }

  end() {
    if (!this.isRunning) return;
    this.isRunning = false;
    clearInterval(this.timerInterval);

    const elapsed = Math.round((Date.now() - this.startTime) / 1000);

    document.getElementById('ar-hud').style.display = 'none';
    const resultsEl = document.getElementById('ar-results');
    if (resultsEl) resultsEl.style.display = 'flex';
    const finalEl = document.getElementById('ar-final-score');
    if (finalEl) finalEl.textContent = this.score;

    this._saveResult(elapsed);
    this.onEnd(this.score, elapsed);
  }

  async _saveResult(elapsed) {
    try {
      await fetch('/ar/save-result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          activity_type: this.activityId,
          results: {
            score:       this.score,
            total_time:  elapsed,
            completed:   true
          }
        })
      });
    } catch (err) {
      console.error('Error guardando resultado:', err);
    }
  }

  exit() {
    this.cleanup();
    window.location.href = '/ar/';
  }

  cleanup() {
    clearInterval(this.timerInterval);
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(t => t.stop());
    }
  }

  _showError(msg) {
    const el = document.getElementById('ar-error');
    if (el) { el.textContent = msg; el.style.display = 'block'; }
  }
}

window.addEventListener('beforeunload', () => {
  if (window._arActivity) window._arActivity.cleanup();
});
