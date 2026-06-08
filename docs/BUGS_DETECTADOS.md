# Bugs Detectados — Pendientes de corrección

Hallazgos colaterales encontrados durante otras tareas. No corregidos para no salirse del alcance.

---

## BUG-001 — main.js sombrea window.MediaRecorder nativo

**Archivo:** `app/static/js/main.js:222`  
**Detectado en:** Investigación de showNotification/ActivityTimer (2026-06-07)

**Problema:** `main.js` define `class MediaRecorder { ... }` y la expone como `window.MediaRecorder = MediaRecorder` (línea 304). Esto sobreescribe el `MediaRecorder` nativo del browser.

`activity_player.html` usa el nativo `new MediaRecorder(stream)` directamente. Si `main.js` se cargara alguna vez, este shadowing rompería la grabación de video.

**Estado actual:** `main.js` no se carga en `base.html` (solo se carga `ar/common.js`), así que el bug no está activo. Pero si se decide incluir `main.js` en el futuro, hay que renombrar la clase.

**Solución sugerida:** Renombrar a `class ActivityMediaRecorder` en `main.js`.

---

## BUG-002 — main.js usa bootstrap.Alert (Bootstrap no cargado)

**Archivo:** `app/static/js/main.js:14,20,67,71`  
**Detectado en:** Investigación de showNotification/ActivityTimer (2026-06-07)

**Problema:** `main.js` llama `new bootstrap.Alert(alert)` en dos lugares:
- `DOMContentLoaded` auto-cierra `.alert` con Bootstrap
- `showNotification` crea divs con `class="alert alert-${type}"` y los cierra con Bootstrap

`base.html` no carga Bootstrap, así que si `main.js` se incluyera, estos llamados lanzarían `ReferenceError: bootstrap is not defined`.

**Estado actual:** `main.js` no se carga, bug no activo.

**Solución sugerida:** Reescribir `main.js` eliminando dependencias de Bootstrap (las funciones equivalentes ya están en `ar/common.js`).
