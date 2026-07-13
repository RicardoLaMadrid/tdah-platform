/**
 * Activa look-controls con magic window (mover el celular mueve la
 * cámara) en móvil. En móvil, look-controls necesita permiso explícito
 * de sensores (DeviceOrientationEvent.requestPermission en iOS 13+).
 * En Android el permiso suele ser implícito, pero igual requerimos una
 * interacción del usuario como red de seguridad.
 * Helper global — usado por ARActivity y por las actividades que no
 * instancian esa clase (secuencia_luces, trail_making, respiracion).
 */
window.initARGyroscope = function () {
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  if (!isMobile) {
    console.log('ℹ️ Desktop detectado — clicks habilitados, giroscopio no aplica');
    return;
  }

  const requestPermissionIfNeeded = async () => {
    if (typeof DeviceOrientationEvent !== 'undefined' &&
        typeof DeviceOrientationEvent.requestPermission === 'function') {
      try {
        const response = await DeviceOrientationEvent.requestPermission();
        return response === 'granted';
      } catch (err) {
        console.error('Error solicitando permiso de sensores:', err);
        return false;
      }
    }
    return true;
  };

  const activateGyroscope = async () => {
    const granted = await requestPermissionIfNeeded();
    if (!granted) {
      console.warn('⚠️ Permiso de sensores denegado');
      return;
    }

    // Nota: <a-camera> no tiene id="ar-camera" en ar_layout.html, se
    // selecciona por tag para no depender de un id que no existe.
    const camera = document.querySelector('a-camera');
    if (camera) {
      camera.setAttribute('look-controls',
        'enabled: true; ' +
        'mouseEnabled: false; ' +
        'touchEnabled: false; ' +
        'magicWindowTrackingEnabled: true'
      );
      console.log('✅ Giroscopio activado en móvil');
    }
  };

  const scene = document.querySelector('a-scene');
  if (!scene) return;

  const setup = () => {
    activateGyroscope();

    const activateOnTouch = () => {
      activateGyroscope();
      document.removeEventListener('touchstart', activateOnTouch);
      document.removeEventListener('click', activateOnTouch);
    };
    document.addEventListener('touchstart', activateOnTouch, { once: true });
    document.addEventListener('click', activateOnTouch, { once: true });
  };

  if (scene.hasLoaded) setup();
  else scene.addEventListener('loaded', setup, { once: true });
};

/**
 * ARActivity — Motor base para actividades de espacio 3D inmersivo.
 * Reemplaza el paradigma "magic window" con cámara por un entorno espacial completo.
 * Las actividades existentes (secuencia, respiracion, trail_making) usan
 * su propio JS standalone y NO instancian esta clase — llaman a
 * window.initARGyroscope() directamente.
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
    window.initARGyroscope();
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

/* ========================================================
   MODO VISOR VR ESTEREOSCÓPICO
   ======================================================== */

let vrModeTimeoutId = null;
let vrModeStartTime = null;
const VR_MODE_MAX_DURATION = 10 * 60 * 1000;  // 10 minutos

/**
 * Activa el modo visor VR: pantalla dividida en 2, fullscreen, cursor 3D
 */
async function toggleVRMode() {
  const scene = document.querySelector('a-scene');
  if (!scene) return;

  const isInVR = document.body.classList.contains('vr-mode-active');

  if (isInVR) {
    exitVRMode();
  } else {
    await enterVRMode();
  }
}

async function enterVRMode() {
  const scene = document.querySelector('a-scene');
  if (!scene) return;

  try {
    // Activar fullscreen
    const elem = document.documentElement;
    if (elem.requestFullscreen) {
      await elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) {
      await elem.webkitRequestFullscreen();
    }

    // Bloquear orientación en landscape si es posible
    if (screen.orientation && screen.orientation.lock) {
      try {
        await screen.orientation.lock('landscape');
      } catch (e) {
        console.log('No se pudo bloquear orientación:', e.message);
      }
    }

    // Marcar body para estilos (ANTES de iniciar el mirror: su loop de
    // rAF se auto-cancela si esta clase no está presente en el primer tick)
    document.body.classList.add('vr-mode-active');

    // NOTA: scene.enterVR() de A-Frame requiere un runtime WebXR real
    // (navigator.xr.requestSession('immersive-vr')). Chrome ya no trae
    // un fallback "cardboard sin hardware", así que en un celular normal
    // sin visor con sensores propios esa llamada siempre falla con
    // NotSupportedError. En su lugar, dividimos la pantalla nosotros
    // mismos con 2 canvas espejo que copian el frame real (sin paralaje,
    // pero el giroscopio ya mueve la única cámara real que ambos copian).
    startStereoMirror();

    // Mostrar botón de salir y timer
    const exitBtn = document.getElementById('ar-vr-exit');
    const timer = document.getElementById('ar-vr-timer');
    if (exitBtn) exitBtn.style.display = 'flex';
    if (timer) timer.style.display = 'flex';

    // Agregar cursor 3D visible en el centro
    addVRCursor(scene);

    // Iniciar timer de 10 minutos
    startVRSessionTimer();

    console.log('✅ Modo Visor VR activado');

  } catch (err) {
    console.error('Error activando modo VR:', err);
    alert('No se pudo activar el modo visor. Verifica que tu navegador soporte fullscreen.');
  }
}

function exitVRMode() {
  const scene = document.querySelector('a-scene');
  if (!scene) return;

  // Salir de fullscreen (solo si seguimos en fullscreen — exitVRMode()
  // también se llama desde el listener de 'fullscreenchange', donde el
  // navegador ya salió de fullscreen por su cuenta, p.ej. al presionar ESC)
  if (document.fullscreenElement || document.webkitFullscreenElement) {
    if (document.exitFullscreen) {
      document.exitFullscreen().catch(e => console.log('Error saliendo fullscreen:', e));
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    }
  }

  // Desbloquear orientación
  if (screen.orientation && screen.orientation.unlock) {
    screen.orientation.unlock();
  }

  // Detener el split de canvas espejo
  stopStereoMirror();

  // Quitar marca del body
  document.body.classList.remove('vr-mode-active');

  // Ocultar botón de salir y timer
  const exitBtn = document.getElementById('ar-vr-exit');
  const timer = document.getElementById('ar-vr-timer');
  if (exitBtn) exitBtn.style.display = 'none';
  if (timer) timer.style.display = 'none';

  // Quitar cursor 3D
  removeVRCursor();

  // Detener timer
  stopVRSessionTimer();

  console.log('🚪 Modo Visor VR desactivado');
}

/**
 * Agrega un cursor 3D fijo en el centro de la vista de la cámara
 */
function addVRCursor(scene) {
  // Eliminar cursor anterior si existe
  removeVRCursor();

  const camera = document.querySelector('a-camera') || document.querySelector('[camera]');
  if (!camera) return;

  // Crear cursor 3D como hijo de la cámara (siempre en el centro de la vista)
  const cursor = document.createElement('a-entity');
  cursor.setAttribute('id', 'vr-3d-cursor');
  cursor.setAttribute('position', '0 0 -1.5');  // 1.5m frente a la cámara

  // Anillo exterior
  const ring = document.createElement('a-ring');
  ring.setAttribute('radius-inner', '0.02');
  ring.setAttribute('radius-outer', '0.03');
  ring.setAttribute('material', 'color: #fbbf24; shader: flat; opacity: 0.9; transparent: true');
  ring.setAttribute('look-at', '[camera]');
  cursor.appendChild(ring);

  // Punto central
  const dot = document.createElement('a-sphere');
  dot.setAttribute('radius', '0.008');
  dot.setAttribute('material', 'color: #fbbf24; shader: flat; emissive: #fbbf24; emissiveIntensity: 1');
  cursor.appendChild(dot);

  camera.appendChild(cursor);
}

function removeVRCursor() {
  const cursor = document.getElementById('vr-3d-cursor');
  if (cursor && cursor.parentNode) {
    cursor.parentNode.removeChild(cursor);
  }
}

/* ========================================================
   SPLIT VISUAL (2 canvas espejo, sin paralaje)
   ======================================================== */

let vrMirrorRAF = null;
let vrMirrorResizeHandler = null;
let vrMirrorInputAttached = false;

/**
 * Muestra 2 canvas que copian, frame a frame, el contenido del canvas
 * real de la escena (que sigue existiendo e interactivo, solo tapado
 * visualmente por este overlay). No hay paralaje: ambos ojos ven
 * exactamente la misma imagen, pero el giroscopio ya mueve la única
 * cámara real que ambos copian, así que la vista sí reacciona al
 * mover la cabeza/celular.
 */
function startStereoMirror() {
  const scene = document.querySelector('a-scene');
  const realCanvas = scene && scene.canvas;
  const container   = document.getElementById('ar-vr-stereo-container');
  const leftCanvas  = document.getElementById('ar-vr-mirror-left');
  const rightCanvas = document.getElementById('ar-vr-mirror-right');
  if (!realCanvas || !container || !leftCanvas || !rightCanvas) return;

  container.style.display = 'flex';

  const syncSize = () => {
    [leftCanvas, rightCanvas].forEach(c => {
      c.width  = c.clientWidth  * (window.devicePixelRatio || 1);
      c.height = c.clientHeight * (window.devicePixelRatio || 1);
    });
  };
  syncSize();
  vrMirrorResizeHandler = syncSize;
  window.addEventListener('resize', vrMirrorResizeHandler);

  const leftCtx  = leftCanvas.getContext('2d');
  const rightCtx = rightCanvas.getContext('2d');

  const draw = () => {
    if (!document.body.classList.contains('vr-mode-active')) return;
    try {
      leftCtx.drawImage(realCanvas, 0, 0, leftCanvas.width, leftCanvas.height);
      rightCtx.drawImage(realCanvas, 0, 0, rightCanvas.width, rightCanvas.height);
    } catch (e) {
      // El primer frame puede no estar listo todavía; se reintenta solo
    }
    vrMirrorRAF = requestAnimationFrame(draw);
  };
  draw();

  attachMirrorInputForwarding(realCanvas, [leftCanvas, rightCanvas]);
}

function stopStereoMirror() {
  const container = document.getElementById('ar-vr-stereo-container');
  if (container) container.style.display = 'none';

  if (vrMirrorRAF) {
    cancelAnimationFrame(vrMirrorRAF);
    vrMirrorRAF = null;
  }
  if (vrMirrorResizeHandler) {
    window.removeEventListener('resize', vrMirrorResizeHandler);
    vrMirrorResizeHandler = null;
  }
}

/**
 * El raycaster de A-Frame ("cursor rayOrigin: mouse") escucha eventos
 * de mouse sobre el canvas REAL. Como visualmente ese canvas queda
 * tapado por los 2 espejos, un click ahí nunca llegaría al canvas real.
 * Esta función reenvía cada evento recibido en un espejo hacia el
 * canvas real, traduciendo la posición proporcionalmente (cada espejo
 * muestra una copia completa de la vista, no una mitad recortada).
 */
function attachMirrorInputForwarding(realCanvas, mirrorCanvases) {
  if (vrMirrorInputAttached) return;
  vrMirrorInputAttached = true;

  const forward = (type) => (e) => {
    if (!document.body.classList.contains('vr-mode-active')) return;

    const mirror     = e.currentTarget;
    const mirrorRect = mirror.getBoundingClientRect();
    const realRect    = realCanvas.getBoundingClientRect();

    const relX = (e.clientX - mirrorRect.left) / mirrorRect.width;
    const relY = (e.clientY - mirrorRect.top)  / mirrorRect.height;

    const evt = new MouseEvent(type, {
      bubbles: true,
      cancelable: true,
      clientX: realRect.left + relX * realRect.width,
      clientY: realRect.top  + relY * realRect.height,
      button: e.button,
      buttons: e.buttons,
    });
    realCanvas.dispatchEvent(evt);
  };

  mirrorCanvases.forEach(mirror => {
    ['mousemove', 'mousedown', 'mouseup', 'click'].forEach(type => {
      mirror.addEventListener(type, forward(type));
    });
  });
}

/**
 * Timer de sesión VR con countdown visual
 */
function startVRSessionTimer() {
  vrModeStartTime = Date.now();
  updateVRTimerDisplay();

  vrModeTimeoutId = setInterval(() => {
    updateVRTimerDisplay();

    const elapsed = Date.now() - vrModeStartTime;
    if (elapsed >= VR_MODE_MAX_DURATION) {
      alert('⏱ Tiempo máximo de sesión alcanzado (10 min). Salir del visor para descansar la vista.');
      exitVRMode();
    }
  }, 1000);
}

function updateVRTimerDisplay() {
  const timerEl = document.getElementById('ar-vr-timer-value');
  if (!timerEl || !vrModeStartTime) return;

  const elapsed = Date.now() - vrModeStartTime;
  const remaining = Math.max(0, VR_MODE_MAX_DURATION - elapsed);

  const minutes = Math.floor(remaining / 60000);
  const seconds = Math.floor((remaining % 60000) / 1000);
  timerEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function stopVRSessionTimer() {
  if (vrModeTimeoutId) {
    clearInterval(vrModeTimeoutId);
    vrModeTimeoutId = null;
  }
  vrModeStartTime = null;
}

// Detectar salida forzada de fullscreen (usuario presionó ESC)
document.addEventListener('fullscreenchange', () => {
  if (!document.fullscreenElement && document.body.classList.contains('vr-mode-active')) {
    exitVRMode();
  }
});

// Exponer globalmente para que otras actividades puedan usarlo
window.toggleVRMode = toggleVRMode;
window.enterVRMode = enterVRMode;
window.exitVRMode = exitVRMode;
