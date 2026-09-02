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

    // Iniciar timer de 10 minutos
    startVRSessionTimer();

    // Habilitar interceptor de volumen del mando como click
    enableVRVolumeClick();

    // Activar cursores sintéticos (uno por ojo)
    enableVRCursors();

    // Mostrar hint sobre el mando por 3 segundos
    const hint = document.createElement('div');
    hint.className = 'ar-vr-hint';
    hint.innerHTML = '🎮 Mové con joystick · <strong>V+</strong> para cazar';
    document.body.appendChild(hint);
    setTimeout(() => hint.remove(), 3000);

    console.log('✅ Modo Visor VR activado');

  } catch (err) {
    console.error('Error activando modo VR:', err);
    alert('No se pudo activar el modo visor. Verifica que tu navegador soporte fullscreen.');
  }
}

function exitVRMode() {
  const scene = document.querySelector('a-scene');
  if (!scene) return;

  // Deshabilitar interceptor de volumen del mando
  disableVRVolumeClick();

  // Desactivar cursores sintéticos
  disableVRCursors();

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

  // Detener timer
  stopVRSessionTimer();

  console.log('🚪 Modo Visor VR desactivado');
}

/* ========================================================
   INTERCEPCIÓN DE TECLAS DE VOLUMEN COMO CLICK EN MODO VR
   Para mandos VR que solo mandan media keys (DESTEK V5 y similares)
   ======================================================== */

let vrVolumeHandlerActive = false;
let lastVolumeClickTime = 0;
const VOLUME_CLICK_COOLDOWN = 200; // ms para evitar dobles clicks

/**
 * Activa la intercepción de volumen como click.
 * Se llama automáticamente al entrar en modo VR.
 */
function enableVRVolumeClick() {
  if (vrVolumeHandlerActive) return;
  vrVolumeHandlerActive = true;

  document.addEventListener('keydown', handleVRVolumeKey, true);
  console.log('🎮 Volumen del mando VR habilitado como click');
}

function disableVRVolumeClick() {
  if (!vrVolumeHandlerActive) return;
  vrVolumeHandlerActive = false;

  document.removeEventListener('keydown', handleVRVolumeKey, true);
  console.log('🎮 Volumen del mando VR deshabilitado');
}

function handleVRVolumeKey(event) {
  // Solo interceptar si estamos en modo VR
  if (!document.body.classList.contains('vr-mode-active')) return;

  const isVolumeUp = event.key === 'AudioVolumeUp'
                  || event.code === 'AudioVolumeUp'
                  || event.keyCode === 175;

  const isVolumeDown = event.key === 'AudioVolumeDown'
                    || event.code === 'AudioVolumeDown'
                    || event.keyCode === 174;

  if (!isVolumeUp && !isVolumeDown) return;

  // Prevenir cambio de volumen del sistema
  event.preventDefault();
  event.stopPropagation();

  // Cooldown para evitar dobles clicks accidentales
  const now = Date.now();
  if (now - lastVolumeClickTime < VOLUME_CLICK_COOLDOWN) return;
  lastVolumeClickTime = now;

  // Tanto V+ como V- disparan click (cazar / seleccionar)
  triggerVRClick();
}

/**
 * Dispara un click sobre el objeto que el raycaster está apuntando.
 *
 * Nota de arquitectura (ver ar_layout.html): el cursor/raycaster
 * ("rayOrigin: mouse") es HERMANO de <a-camera>, no hijo, y sigue al
 * cursor del SISTEMA (que el joystick del mando mueve), no al cursor 3D
 * dorado central (que es solo visual). Por eso apuntamos con lo que el
 * raycaster tiene intersectado en este instante.
 *
 * Excepción: si el magnetismo tiene un elemento capturado (el que el
 * usuario VE con halo), ese gana. El rayo sigue al mouse crudo, que puede
 * estar unos pixels fuera del objeto justo cuando el cursor ya se enganchó.
 */
function triggerVRClick() {
  if (currentCapturedElement && currentCapturedElement.isConnected) {
    console.log('🎯 Click VR sobre target capturado:',
      currentCapturedElement.tagName, currentCapturedElement.className);
    currentCapturedElement.emit('click', {}, true);
    return;
  }

  const rayEl = document.querySelector('[raycaster]');
  const raycaster = rayEl && rayEl.components && rayEl.components.raycaster;
  const hits = raycaster && raycaster.intersectedEls;

  if (hits && hits.length > 0) {
    // El objeto más cercano bajo el rayo. Emitimos con bubbles: true
    // porque el listener de click suele estar en el wrapper padre
    // mientras que el raycaster intersecta el hijo con geometría
    // (ver ARVisuals.syncClickable en ar_visuals.js).
    const target = hits[0];
    console.log('🎯 Click VR sobre:', target.tagName, target.className);
    target.emit('click', {}, true);
    return;
  }

  console.log('🎯 Click VR: sin objeto bajo el cursor del mando');
}

// Exponer para debugging desde consola
window.enableVRVolumeClick = enableVRVolumeClick;
window.disableVRVolumeClick = disableVRVolumeClick;
window.triggerVRClick = triggerVRClick;

/* ========================================================
   CURSORES SINTÉTICOS PARA MODO VR
   Dibuja un cursor visible en cada ojo, siguiendo la posición
   del mouse del sistema (movido por el joystick del mando VR).
   Reemplaza al cursor del sistema (que solo se ve en un ojo y
   es la flechita negra de Android).
   ======================================================== */

let vrCursorHandlerActive = false;

function enableVRCursors() {
  if (vrCursorHandlerActive) return;
  vrCursorHandlerActive = true;

  const leftCursor = document.getElementById('vr-cursor-left');
  const rightCursor = document.getElementById('vr-cursor-right');

  if (leftCursor) leftCursor.style.display = 'block';
  if (rightCursor) rightCursor.style.display = 'block';

  document.addEventListener('mousemove', updateVRCursors, true);

  // Inicializar en el centro
  positionVRCursors(window.innerWidth / 2, window.innerHeight / 2);

  console.log('🎯 Cursores sintéticos VR activados');
}

function disableVRCursors() {
  if (!vrCursorHandlerActive) return;
  vrCursorHandlerActive = false;

  const leftCursor = document.getElementById('vr-cursor-left');
  const rightCursor = document.getElementById('vr-cursor-right');

  if (leftCursor) leftCursor.style.display = 'none';
  if (rightCursor) rightCursor.style.display = 'none';

  document.removeEventListener('mousemove', updateVRCursors, true);
  setVRCursorsCapturedState(false, null);
  console.log('🎯 Cursores sintéticos VR desactivados');
}

/* --- Magnetismo del cursor --------------------------------------------
   Con el joystick del mando VR es muy difícil frenar justo encima de un
   asteroide. Cuando el cursor entra en el radio de atracción del
   clickable más cercano, lo "engancha" interpolando hacia su centro y
   marca el estado capturado (cursores verdes + halo 3D en el objetivo).
   ---------------------------------------------------------------------- */

const MAGNET_RADIUS = 80;    // px de radio de atracción (espacio del canvas real)
const MAGNET_STRENGTH = 0.6; // 0 = sin tirón, 1 = pega al centro

let currentCapturedElement = null;

function updateVRCursors(event) {
  // Solo activo en modo VR
  if (!document.body.classList.contains('vr-mode-active')) return;

  // attachMirrorInputForwarding reenvía cada mousemove al canvas real como
  // evento sintético, así que cada movimiento llega dos veces (crudo +
  // reenviado, con la X ya duplicada). Nos quedamos solo con el crudo y
  // hacemos la conversión nosotros para no depender del orden de entrega.
  if (!event.isTrusted) return;

  const point = mirrorToSceneCoords(event.clientX, event.clientY);
  let cursorX = point.x;
  let cursorY = point.y;

  const nearestTarget = findNearestClickableOnScreen(cursorX, cursorY);

  if (nearestTarget && nearestTarget.distance < MAGNET_RADIUS) {
    // Cuanto más cerca del target, más fuerte tira
    const proximityFactor = 1 - (nearestTarget.distance / MAGNET_RADIUS);
    const pullStrength = MAGNET_STRENGTH * proximityFactor;

    cursorX += (nearestTarget.centerX - cursorX) * pullStrength;
    cursorY += (nearestTarget.centerY - cursorY) * pullStrength;

    setVRCursorsCapturedState(true, nearestTarget.element);
  } else {
    setVRCursorsCapturedState(false, null);
  }

  positionVRCursors(cursorX, cursorY);
}

/**
 * Convierte coordenadas de viewport (donde está el mouse físico, encima de
 * uno de los 2 espejos) al espacio del canvas REAL de la escena.
 *
 * Cada espejo mide 50% del ancho y dibuja la vista COMPLETA comprimida
 * (ver startStereoMirror), así que la X dentro de un espejo vale el doble
 * en el canvas real. Es el mismo espacio en el que trabaja el raycaster.
 */
function mirrorToSceneCoords(clientX, clientY) {
  const halfWidth = window.innerWidth / 2;
  const inLeftEye = clientX < halfWidth;
  return {
    x: (inLeftEye ? clientX : clientX - halfWidth) * 2,
    y: clientY,
  };
}

/**
 * Encuentra el elemento .clickable más cercano al cursor en pantalla,
 * proyectando su posición 3D a coordenadas 2D del canvas real.
 */
function findNearestClickableOnScreen(cursorX, cursorY) {
  const scene = document.querySelector('a-scene');
  if (!scene || !scene.hasLoaded) return null;

  const camera = scene.camera;
  const canvas = scene.canvas;
  if (!camera || !canvas) return null;

  const rect = canvas.getBoundingClientRect();

  // ARVisuals._mirrorClickable copia la clase al hijo con geometría, así
  // que cada objeto aparece 2 veces. Nos quedamos con el wrapper.
  const candidates = new Set();
  document.querySelectorAll('.clickable').forEach(el => {
    const parent = el.parentElement;
    candidates.add(parent && parent.classList.contains('clickable') ? parent : el);
  });

  const worldPos = new THREE.Vector3();
  const worldScale = new THREE.Vector3();

  let nearest = null;
  let minDistance = Infinity;

  candidates.forEach(el => {
    const object3D = el.object3D;
    if (!object3D || !object3D.visible) return;

    // Ignorar objetos que todavía están apareciendo (scale animado desde 0)
    object3D.getWorldScale(worldScale);
    if (Math.max(worldScale.x, worldScale.y, worldScale.z) < 0.05) return;

    object3D.getWorldPosition(worldPos);
    const screenPos = worldPos.clone().project(camera);

    // Solo elementos frente a la cámara
    if (screenPos.z > 1) return;

    const canvasX = (screenPos.x + 1) / 2 * rect.width + rect.left;
    const canvasY = (-screenPos.y + 1) / 2 * rect.height + rect.top;

    const dx = canvasX - cursorX;
    const dy = canvasY - cursorY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < minDistance) {
      minDistance = distance;
      nearest = { element: el, centerX: canvasX, centerY: canvasY, distance };
    }
  });

  return nearest;
}

/**
 * Estado visual de "capturado" (el equivalente a la manito del sistema):
 * cursores verdes más grandes + halo dorado pulsante sobre el objetivo.
 */
function setVRCursorsCapturedState(isCaptured, targetElement) {
  const target = isCaptured ? targetElement : null;
  if (target === currentCapturedElement) return;

  const leftCursor = document.getElementById('vr-cursor-left');
  const rightCursor = document.getElementById('vr-cursor-right');
  if (leftCursor) leftCursor.classList.toggle('captured', !!target);
  if (rightCursor) rightCursor.classList.toggle('captured', !!target);

  if (currentCapturedElement) removeTargetHalo(currentCapturedElement);

  if (target) {
    addTargetHalo(target);
    // Vibración leve solo al cambiar de objetivo, nunca continua
    if ('vibrate' in navigator) navigator.vibrate(15);
  }

  currentCapturedElement = target;
}

/**
 * Halo dorado pulsante alrededor del elemento capturado. El radio se
 * deriva de la geometría real (los asteroides van de 0.2 a 0.4).
 */
function addTargetHalo(element) {
  if (element.querySelector('.vr-target-halo')) return;

  const radius = computeHaloRadius(element);

  const halo = document.createElement('a-ring');
  halo.classList.add('vr-target-halo');
  halo.setAttribute('radius-inner', (radius * 1.25).toFixed(3));
  halo.setAttribute('radius-outer', (radius * 1.6).toFixed(3));
  halo.setAttribute('material',
    'shader: flat; color: #fbbf24; opacity: 0.8; transparent: true; side: double');
  halo.setAttribute('look-at', '[camera]');
  halo.setAttribute('animation',
    'property: scale; from: 1 1 1; to: 1.2 1.2 1.2; dur: 800; dir: alternate; loop: true; easing: easeInOutQuad');

  element.appendChild(halo);
}

function removeTargetHalo(element) {
  const halo = element.querySelector('.vr-target-halo');
  if (halo && halo.parentNode) halo.parentNode.removeChild(halo);
}

/**
 * Radio del objeto en unidades LOCALES del wrapper. Usamos la boundingSphere
 * de la geometría (no el bounding box en mundo) para que la animación de
 * spawn (scale 0 → 1) no achique el halo, que ya hereda esa escala.
 */
function computeHaloRadius(element) {
  const object3D = element.object3D;
  let maxRadius = 0;

  if (object3D) {
    object3D.traverse(node => {
      const geometry = node.geometry;
      if (!geometry) return;
      if (!geometry.boundingSphere) geometry.computeBoundingSphere();
      if (!geometry.boundingSphere) return;

      const nodeScale = Math.max(
        Math.abs(node.scale.x), Math.abs(node.scale.y), Math.abs(node.scale.z)
      ) || 1;
      maxRadius = Math.max(maxRadius, geometry.boundingSphere.radius * nodeScale);
    });
  }

  return maxRadius > 0.01 ? maxRadius : 0.4;
}

/**
 * Coloca los 2 cursores. Recibe coordenadas del canvas REAL (ancho
 * completo) y las comprime al 50% de cada ojo, igual que hace el espejo
 * al dibujar el frame. Así el cursor cae exactamente sobre el punto de la
 * escena al que apunta el rayo.
 */
function positionVRCursors(x, y) {
  const leftCursor = document.getElementById('vr-cursor-left');
  const rightCursor = document.getElementById('vr-cursor-right');
  if (!leftCursor || !rightCursor) return;

  const halfWidth = window.innerWidth / 2;
  const eyeX = x * 0.5;

  leftCursor.style.left = eyeX + 'px';
  rightCursor.style.left = (eyeX + halfWidth) + 'px';
  leftCursor.style.top = y + 'px';
  rightCursor.style.top = y + 'px';
}

// Exponer para debugging
window.enableVRCursors = enableVRCursors;
window.disableVRCursors = disableVRCursors;

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
