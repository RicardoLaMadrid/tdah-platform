# Auditoría QA — 2026-06-07

## Resumen ejecutivo
- **5 de 12 secciones** pasan al 100%
- **4 bugs críticos** detectados (impiden defensa o rompen flujo central)
- **8 bugs importantes** detectados (dan mala impresión)
- **7 issues menores** detectados (cosmético/técnico)
- **8 pantallas** con mezcla de Bootstrap residual + Tailwind

---

## Estado del servidor al arrancar

Análisis estático del arranque (`run.py` → `create_app()`):

- La app imprime `"APLICACION INICIALIZADA CORRECTAMENTE"` al arrancar.
- El blueprint `oauth_bp` se registra con `try/except ImportError` — si Authlib no está instalado, el OAuth queda silenciosamente deshabilitado (no lanza error en arranque).
- Los blueprints de assessments (`vision_bp`, `audio_bp`, `stroop_bp`, `gonogo_bp`) también están en bloque `try/except` — si falta alguna dependencia (opencv, numpy, SpeechRecognition), ese blueprint no se registra sin advertencia visible.
- **matplotlib** se usa en `vision/routes.py` (importado en nivel de módulo), pero **no está en `requirements.txt`**. Si no está instalado el servidor no arranca en absoluto.
- La carga de los clasificadores Haar de OpenCV ocurre al importar `vision/routes.py` — si falla, el blueprint de visión no se registra y `/vision/` da 404 en silencio.
- `WHATSAPP_ENABLED` y `OPENAI_API_KEY` ausentes en `.env` solo provocan avisos impresos, no errores de arranque.

**Warnings probables al arrancar (sin .env completo):**
```
⚠️  Google OAuth no configurado (faltan GOOGLE_CLIENT_ID/SECRET)
```
Resto del arranque: limpio.

---

## Secciones — Resultado detallado

### Sección 1: Autenticación — ✅ OK

| Item | Estado | Detalle |
|------|--------|---------|
| `/auth/login` renderiza | ✅ | Extiende `auth_base.html` → existe en `shared/templates` |
| Login por username o email | ✅ | `User.query.filter((username==x) \| (email==x))` |
| Login fallido muestra mensaje | ✅ | `flash('Credenciales inválidas.', 'danger')` |
| Logout redirige a login | ✅ | `redirect(url_for('auth.login'))` |
| Botón "Continuar con Google" condicional | ✅ | `{% if config.GOOGLE_CLIENT_ID %}` — aparece solo si hay key |
| Registro NO autoservicio | ✅ | `/auth/register` solo GET, renderiza aviso sin form de POST |
| Remember me 30 días | ✅ | `login_user(user, remember=remember, duration=timedelta(days=30))` |
| Redirect post-login por rol | ✅ | `role_redirects` en `auth.dashboard` |
| **ISSUE**: Rol 'parent' en dashboard | ⚠️ | `auth.dashboard` intenta `url_for('parent.index')` — blueprint `parent` NO existe → `BuildError` si un usuario con rol `parent` logra iniciar sesión |

**Diagnóstico bug auth:** El ENUM `role` en el modelo `User` todavía incluye `'parent'`. Si en la BD hay algún usuario con ese rol, el login rompe con `BuildError` al intentar `url_for('parent.index')`.

---

### Sección 2: Navegación — ⚠️ PARCIAL

**Sidebar Admin** (4 links):
- Dashboard → `admin.index` ✅
- Usuarios → `admin.users` ✅
- Asignaciones → `admin.assignments` ✅
- Estadísticas → `admin.reports` ✅

**Sidebar Teacher** (4 links):
- Inicio → `teacher.index` ✅
- Estudiantes → `teacher.students` ✅
- Actividades → `teacher.activities` ✅
- Reportes → `teacher.reports` ✅

**Sidebar Student** (5 links):
- Inicio → `student.index` ✅
- Mis Tests → `student.tests_index` ✅
- Mis Actividades → `student.activities` ✅
- Mi Progreso → `student.progress` ✅
- Actividades AR → `ar.index` ✅

**Logo en sidebar** → `home_url()` context processor — ✅ funciona por rol.

**Topbar** → `current_user.username` + dropdown con perfil y logout ✅

**Endpoints huérfanos** (registrados pero fuera de sidebar):
- `/admin/users/create` — accesible desde botón en `/admin/users`
- `/admin/inscribir-alumno` — accesible desde botón en `/admin/users`
- `/admin/users/<id>/edit` — desde tabla
- `/teacher/students/<id>` — desde lista de estudiantes
- `/teacher/activities/create`
- `/teacher/reports/create/<session_id>`
- `/teacher/sessions/<id>`
- Todos los endpoints de tests: `/vision/`, `/audio/`, `/stroop/`, `/gonogo/` — accesibles desde `student.tests_index`

**Links rotos en sidebar:** Ninguno. Todos los 5 links del sidebar student existen como endpoints registrados (incluido `ar.index`).

**Issue UX:** El sidebar student incluye `ar.index` que lleva a un template que aún usa Bootstrap legacy (`ar/index.html` con clases `container`, `card`, `badge`, `row`, `col-md-*`), mientras el resto del panel student usa Tailwind puro — **quiebre visual grave**.

---

### Sección 3: Panel Admin — ✅ OK

| Pantalla | Estado | Notas |
|----------|--------|-------|
| `/admin/` — métricas | ✅ | Todas las queries tienen fallback (`or 0`); stats bien definidas |
| `/admin/users` — lista | ✅ | Filtros HTMX + Alpine funcionan por diseño |
| Filtros usuarios | ✅ | `filter_users_query()` en helpers.py bien implementado |
| `/admin/inscribir-alumno` | ✅ | Wizard POST bien estructurado con validaciones |
| `/admin/users/<id>/edit` | ⚠️ | Usa `User.query.get_or_404()` — deprecated en SQLAlchemy 2.x (funciona en Flask-SQLAlchemy 3.1 pero es legacy) |
| `/admin/assignments` | ✅ | |
| Eliminar usuario | ✅ | Protección contra auto-eliminación |
| **HTMX auto-refresh** dashboard | ⚠️ | `hx-trigger="every 30s"` hace GET completo a `/admin/` — si hay muchos usuarios puede ser costoso |

---

### Sección 4: Panel Teacher — ⚠️ PARCIAL

| Item | Estado | Detalle |
|------|--------|---------|
| `/teacher/` dashboard | ✅ | Grid de alumnos con filtros HTMX |
| Click alumno → detalle | ✅ | `/teacher/students/<id>` con verificación de teacher_id |
| `/teacher/activities` | ✅ | |
| `/teacher/reports` | ✅ | |
| Crear reporte | ⚠️ | Solo crea reporte si hay `session_id` — no hay ruta para crear reporte sin sesión previa. El link "crear reporte" desde `teacher.reports` no existe en el sidebar ni en ese template: solo se puede desde una sesión. |
| Botón "Generar análisis con IA" | ⚠️ | Llama a `ai_service` que requiere `OPENAI_API_KEY`. Si no está configurada, retorna error 500 con mensaje en JSON — no hay manejo en el frontend para mostrar mensaje amigable al docente. El `AIActivityGenerator` sí tiene fallback local. |
| Enviar WhatsApp | ✅ | Guarda resultado aunque WhatsApp falle; notificación interna siempre se crea |
| PDF descarga | ✅ | `reportlab` en requirements |

---

### Sección 5: Panel Student — ⚠️ PARCIAL

| Item | Estado | Detalle |
|------|--------|---------|
| `/student/` — dashboard | ✅ | Mascota Tito, racha, reto del día, grid 2×2 |
| Mascota Tito | ✅ | SVG inline, Alpine.js bubble |
| Reto del día lógico | ✅ | Prioriza tests incompletos en orden Stroop→GoNoGo→Visión→Audio |
| Selector de tests (`/student/tests`) | ✅ | 4 cards grandes con contador de completados |
| Click en cada test → instrucciones | ✅ | Visión, Audio, Stroop, GoNoGo — todos renderizan |
| Actividades AR (botón) | ⚠️ | Botón "Actividades AR" en dashboard student va a `student.activities` (actividades clásicas), no a `ar.index` — confusión semántica |
| `/student/progreso` | ⚠️ | Solo muestra datos de tests de visión y audio (no Stroop ni Go/No-Go) — el código `calcular_tendencias()` y las gráficas solo procesan `vision_data` y `audio_data` |
| `get_student_profile()` | ✅ | Helper robusto para todos los casos lazy/list/direct |

**Bug progreso:** La página `/student/progreso` llama a `Report.query.filter(...report_type == 'vision_test')` y `report_type == 'audio_test'` pero no incluye `stroop_test` ni `gonogo_test`. Los tests que más se ejecutan (Stroop y GoNoGo, que persisten en BD) quedan invisibles en el historial del estudiante.

---

### Sección 6: Tests Cognitivos — ⚠️ PARCIAL

#### Test Stroop ✅
- Instrucciones: ✅ template Tailwind puro, bien diseñado
- Botón "Empezar" → Alpine `phase: 'intro'` → `phase: 'test'` ✅
- Estado persistido en BD (`active_test_sessions`) ✅ — sobrevive hot-reload
- `finish_test` analiza y redirige a resultados ✅
- Score no negativo: precisión calculada como `correctos/total * 100` — rango 0–100 ✅
- `print()` debug en `analizar_resultados()` (abundante) ⚠️

#### Test Go/No-Go ✅
- Estructura idéntica al Stroop, mismas garantías ✅
- `print()` debug abundante ⚠️

#### Test Visión ⚠️
- Instrucciones: ✅ template Tailwind limpio
- Estado **en memoria** (`test_sessions = {}`) — comentario en código acepta que si el servidor se reinicia el test se pierde — **diferencia vs. Stroop/GoNoGo que usan BD** ⚠️
- **`matplotlib` no está en `requirements.txt`** — si no está instalado, el módulo `vision/routes.py` no importa y el blueprint no se registra → `/vision/` da 404 ❌
- Heatmap se guarda en `app/static/uploads/heatmaps/` — directorio cubierto por `.gitignore` (correcto)
- Score: `confianza = int(clasificacion_primaria[1]['probabilidad'])` — rango 0–100 ✅
- `print()` debug muy abundante (función `_calcular_scores_detallados` imprime en cada frame procesado) ❌

#### Test Audio ⚠️
- Instrucciones: ✅ template Tailwind limpio con visualizador de micrófono
- Requiere `SpeechRecognition` + `pydub` + acceso a internet (Google Speech API) ✅ en requirements
- **`ffmpeg` puede ser requerido por `pydub`** para convertir webm — no incluido en requirements ni mencionado en docs ⚠️
- Estado parcialmente en BD (crea `ActiveTestSession` en `start_test`, pero el análisis real ocurre en `upload_audio` sin necesitar el estado previo) ✅
- Si Google Speech API falla → mensaje de error claro devuelto al usuario ✅
- `print()` debug abundante en `_calcular_scores_detallados` ⚠️

---

### Sección 7: Actividades AR — ❌ FALLA (diagnóstico específico)

#### Causa raíz de "al ingresar no hace nada"

**El problema primario:** `ar/index.html` extiende `base.html` pero pertenece al panel student. `base.html` es el layout Tailwind con sidebar. Sin embargo, `ar/caza_objetos.html`, `ar/respiracion.html` y `ar/secuencia_luces.html` también extienden `base.html` (no `_layouts/student_layout.html`) — la escena A-Frame está en `{% block content %}` que normalmente tiene padding y layout de columna flex, que puede interrumpir la visualización full-screen del canvas AR.

**Problemas específicos por actividad:**

**1. Caza de Objetos (`ar/caza_objetos.html`)**
- Extiende `base.html` (layout Tailwind con sidebar) ⚠️
- A-Frame CDN cargado correctamente: `https://aframe.io/releases/1.4.0/aframe.min.js` ✅
- `<a-scene>` con `display:none` inicial — se muestra al `startGame()` ✅
- Clases Bootstrap mezcladas: `btn btn-success`, `col-4`, `row` en `#ui-overlay` — si Bootstrap **no está cargado** en `base.html` (que usa Tailwind), estos estilos no aplican → el overlay queda sin formato
- **Verificación crítica:** `base.html` carga `output.css` (Tailwind) pero NO carga Bootstrap CSS. Las clases `btn`, `col-4`, `row`, `display-1` etc. en `caza_objetos.html` NO tienen estilos → los botones aparecen sin estilo y el layout se rompe, pero **el juego sí funciona** funcionalmente (JS es independiente de CSS)
- El `<a-scene embedded>` con CSS `overflow: hidden; width: 100vw` dentro del layout Tailwind (`flex-col`, padding de sidebar) puede causar que la escena no ocupe toda la pantalla — **este es el problema visual de "no hace nada"**: la escena se renderiza pero queda oculta detrás del sidebar o con 0px de alto
- `saveResults()` hace `fetch` a `url_for('ar.save_result')` correctamente ✅

**2. Secuencia de Luces (`ar/secuencia_luces.html`)**
- Extiende `base.html` ⚠️
- **No usa A-Frame** — usa CSS puro con `background: #000` y divs `.light-orb` ✅ (funciona sin WebXR)
- El juego funciona completamente en 2D — **no es AR real** ✅/⚠️
- Clases Bootstrap: `text-center`, `badge`, `btn` — sin Bootstrap cargado, botones sin estilos
- `saveResults()` hace fetch a `ar.save_result` ✅

**3. Respiración Guiada (`ar/respiracion.html`)**
- Extiende `base.html` ⚠️
- `background: linear-gradient(135deg, ...)` en body — el sidebar de `base.html` sigue visible, cortando el fondo
- **No usa A-Frame** — animación CSS pura ✅
- Clases Bootstrap: `h5`, `mb-2`, `mt-3` — sin Bootstrap = tamaños de fuente por defecto del navegador
- Funciona en JS puro ✅

**4. Trail Making (`ar/trail_making.html`)**
- **No hay ruta registrada en `ar/routes.py` para Trail Making** ❌
- El template existe pero no hay endpoint `/ar/trail-making` ni enlace en `ar/index.html`
- `ar/index.html` solo muestra 3 actividades (caza, secuencia, respiración) — Trail Making es huérfano total

**Resumen diagnóstico AR:**
| Problema | Impacto |
|----------|---------|
| Templates extienden `base.html` con sidebar visible | Escena AR ocupa espacio reducido, parece "en blanco" |
| Bootstrap classes sin Bootstrap cargado | Botones sin estilos, layout roto visualmente |
| A-Frame `embedded` dentro de flex-column Tailwind | Canvas AR puede quedar con 0px de alto |
| Trail Making sin ruta registrada | 404 si se accede directamente |
| `ar/index.html` usa Bootstrap legacy completo | Quiebre visual total vs. Tailwind student panel |

---

### Sección 8: Generación de reportes con IA — ⚠️ PARCIAL

| Item | Estado | Detalle |
|------|--------|---------|
| `OPENAI_API_KEY` en config.py | ✅ | `os.environ.get('OPENAI_API_KEY')` — no obligatoria al arrancar |
| `.env.example` tiene la key | ✅ | `OPENAI_API_KEY=sk-tu-key-aqui` |
| `AIService` importa correctamente | ✅ | `app/reports/ai_service.py` con instancia global `ai_service` |
| `AIActivityGenerator` con fallback | ✅ | Si no hay API key, usa banco local de actividades |
| Click "Generar análisis IA" (POST `/teacher/api/ai-suggestions`) | ⚠️ | El endpoint existe, llama a `ai_service.generate_teacher_report()`. Si `OPENAI_API_KEY` es None, lanza `ValueError("OPENAI_API_KEY no configurada")` → el endpoint devuelve `{'error': ...}` con status 500, pero el frontend no tiene manejo visible del error — el botón simplemente no hace nada observable para el usuario |
| Respuesta estructurada | ✅ | JSON con `resumen_ejecutivo`, `fortalezas`, `recomendaciones`, etc. |
| Formato de actividad generada | ✅ | `AIActivityGenerator.generate_activity()` tiene fallback local |

---

### Sección 9: Notificaciones — ✅ OK

| Item | Estado | Detalle |
|------|--------|---------|
| Modelo `Notification` | ✅ | En `app/core/models/notification.py` — campos correctos |
| `notify_tutor_of_student()` | ✅ | Implementado correctamente, sin dependencia de tabla `parents` |
| `notify_parents_of_student()` | ✅ | Alias de backward-compat que delega al método anterior |
| Notificación al completar test | ✅ | Todos los blueprints de test llaman `Notification.notify_parents_of_student()` en bloque try/except |
| WhatsApp lógica | ✅ | `WHATSAPP_ENABLED` requerido + Twilio credentials; si falta, imprime aviso y retorna False |
| No crashea si WhatsApp falla | ✅ | Try/except en `notify_tutor_of_student()` |
| **ISSUE**: `app/models/notification.py` | ⚠️ | Es solo un re-export — importaciones en algunos routes usan `app.models.notification` (routes de AR, audio, vision), otros usan `app.core.models.notification` (teacher). Funcionan igual pero inconsistente |

---

### Sección 10: Aspectos visuales y UX — ❌ FALLA

#### Bootstrap residual (crítico para consistencia visual)

Hay **69 ocurrencias** de clases `class="btn` y **789 ocurrencias** de patrones Bootstrap en templates. Las páginas afectadas se dividen en dos categorías:

**Templates que usan Bootstrap SIN que esté cargado en `base.html`:**
- `ar/caza_objetos.html` — `btn btn-success`, `col-4`, `row`, `display-1`
- `ar/index.html` — `container-fluid`, `card`, `badge`, `row`, `col-md-*`
- `ar/respiracion.html` — clases de tamaño Bootstrap
- `ar/secuencia_luces.html` — `badge`, `btn`
- `ar/trail_making.html` — `btn`
- `student/progress.html` — mezcla Tailwind + Bootstrap legacy
- `student/activities.html` — mezcla
- `student/activity_detail.html` — mezcla
- `student/activity_player.html` — mezcla
- `teacher/session_detail.html` — `btn`
- `teacher/create_activity.html` — `btn`
- `admin/assignments.html` — Bootstrap select, table clases
- `admin/edit_user.html` — `btn`, form groups Bootstrap
- `admin/parent_links.html` — Bootstrap completo

**Templates Tailwind puros (bien migrados):**
- Login, dashboard admin, dashboard teacher, dashboard student, test_stroop, test_audio, test_gonogo, test_vision, tests_index, resultado_*.html

#### Otros issues UX

| Issue | Archivos afectados |
|-------|--------------------|
| Empty states sin mensaje en tablas | `teacher/reports.html`, `teacher/activities.html` cuando hay 0 resultados muestran tabla vacía |
| Mascota Tito no aparece en páginas de test (sidebar oculto con CSS) | `test_stroop.html` tiene `aside { display: none !important }` — pero `{% block extra_js %}` donde vive Tito también está bloqueado |
| AR index visualmente roto (Bootstrap sin cargar) | `ar/index.html` |
| Texto mínimo < 14px en topbar | `text-xs` = 12px — en labels del topbar |

---

### Sección 11: Estado de la BD — ⚠️ PARCIAL

#### Modelos detectados

| Modelo | Tabla | Estado |
|--------|-------|--------|
| User | `users` | ✅ — ENUM incluye 'parent' (no eliminado del ENUM) |
| Student | `students` | ✅ — tiene campos `tutor_*` |
| Parent | `parents` | ⚠️ — **modelo y tabla siguen existiendo** en `app/core/models/parent.py` y se importan en `app/__init__.py` |
| ParentStudent | `parent_student` | ⚠️ — tabla y modelo siguen existiendo |
| Activity | `activities` | ✅ |
| Session | `sessions` | ✅ |
| Report | `reports` | ✅ — campos `tipo_tdah`, `confianza` presentes |
| Notification | `notifications` | ✅ |
| ActiveTestSession | `active_test_sessions` | ✅ |
| Badge | `badges` | ✅ (modelo en `app/core/models/badge.py`) |

#### Migraciones
- **No hay directorio `migrations/versions/`** — no se encontró ningún archivo de migración. El esquema se crea por `init_database.py` o `db.create_all()`, no por Alembic.
- Riesgo: los campos nuevos (`tutor_*`, `active_test_sessions`) pueden no existir en la BD de producción si se usó el SQL inicial.

#### Problemas críticos de BD

1. **ENUM 'parent' en User.role todavía presente** — el modelo `User` en `app/core/models/user.py` declara `db.Enum('admin', 'teacher', 'student', 'parent')`. Si la BD MySQL tiene el ENUM sin 'parent', Flask-SQLAlchemy no validará esto en consultas pero intentar insertar un usuario con role='parent' fallará en BD. Si la BD tiene el ENUM con 'parent', el bug de `auth.dashboard` aplica.

2. **Tablas `parents` y `parent_student` siguen existiendo** — importadas en `app/__init__.py` (`from app.core.models import ... parent`). Flask-Migrate las detectará como parte del esquema. No son huérfanas en código pero sí son conceptualmente obsoletas.

3. **Campo `age` en Student vs. comentario en audio** — `audio/routes.py` línea 275 dice "NOTA: El campo 'age' no existe en el modelo actual" pero `app/core/models/student.py` sí tiene `age = db.Column(db.Integer)`. El comentario es incorrecto — el campo existe y está bien.

---

### Sección 12: Calidad del código — ⚠️ PARCIAL

#### `print()` de debug — conteo

| Archivo | Ocurrencias `print()` | Tipo |
|---------|----------------------|------|
| `app/core/models/student.py` | 21 | Debug de algoritmo TDAH — intencionales |
| `app/assessments/audio/routes.py` | 19 | Debug de análisis — algunos intencionales, exceso en producción |
| `app/assessments/vision/routes.py` | 24 | Debug por frame procesado — exceso grave |
| `app/assessments/stroop/routes.py` | 10 | Debug de análisis |
| `app/assessments/gonogo/routes.py` | 14 | Debug de análisis |
| `app/auth/oauth.py` | 4 | Informativos de configuración OAuth |
| `app/notifications/whatsapp.py` | 5 | Informativos/errores — aceptables |
| Resto | ~23 | Mixtos |

**Total: ~120 `print()` statements** — muchos de los que están dentro de loops de procesamiento por frame (visión) y por trial (Stroop/GoNoGo) inundarán la consola del servidor durante una sesión de test real.

#### `requirements.txt` — FALTA matplotlib

```
matplotlib  ← no está en requirements.txt
```

`app/assessments/vision/routes.py` líneas 8-10:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

**Si matplotlib no está instalado, el servidor no puede registrar el blueprint de visión y `/vision/` retorna 404.**

#### Otros

| Item | Estado |
|------|--------|
| TODOs críticos | ✅ Solo comentarios aclaratorios, ningún TODO bloqueante |
| `.env.example` actualizado | ✅ Tiene todas las variables necesarias |
| `.gitignore` cubre venv, __pycache__, .env, uploads, output.css | ✅ |
| `requirements.txt` sincronizado | ⚠️ Falta `matplotlib` |
| Uso de `User.query.get_or_404()` (deprecated SQLAlchemy 2.x) | ⚠️ En `admin/routes.py` líneas 151, 208 |
| Importaciones duales `app.models.*` vs `app.core.models.*` | ⚠️ Ambos caminos funcionan (re-exports) pero inconsistente |

---

## Bugs por prioridad

### CRITICOS (impiden defender o rompen flujo central)

1. **matplotlib no está en requirements.txt** — Archivo: `requirements.txt`, `app/assessments/vision/routes.py:8`. Si el entorno no tiene matplotlib instalado manualmente, el blueprint de visión no se registra y `/vision/` da 404. El Test de Visión es una de las 4 evaluaciones centrales de la tesis. Fix estimado: 1 línea en requirements.txt.

2. **AR templates heredan base.html con sidebar — escena AR queda invisible** — Archivos: `app/templates/ar/caza_objetos.html`, `ar/respiracion.html`, `ar/secuencia_luces.html`. El `<a-scene embedded>` dentro del flex layout de Tailwind (sidebar + content column) queda con dimensiones incorrectas o 0px de alto. Es la causa raíz del "no hace nada". Fix estimado: cambiar `{% extends 'base.html' %}` por un layout full-screen sin sidebar en esos 3 templates.

3. **Bug auth.dashboard con rol 'parent'** — Archivo: `app/auth/routes.py:83`. Si existe un usuario con `role='parent'` en BD, el login genera `BuildError` al intentar `url_for('parent.index')` — blueprint inexistente. Fix estimado: eliminar entrada `'parent': 'parent.index'` del dict `role_redirects` y el ENUM de User.

4. **Progreso del estudiante no incluye Stroop ni Go/No-Go** — Archivo: `app/student/routes.py:279-358`. Los tests cognitivos más usados (Stroop y GoNoGo) no aparecen en `/student/progreso` — solo muestra visión y audio. El historial real del estudiante está incompleto. Fix estimado: agregar queries y procesamiento para `stroop_test` y `gonogo_test` en la función `progress()`.

### IMPORTANTES (notan, dan mala impresión)

1. **`ar/index.html` usa Bootstrap legacy completo** — Archivo: `app/templates/ar/index.html`. Usa `container-fluid`, `card`, `badge`, `row`, `col-md-*` sin Bootstrap cargado → botones y cards sin estilos. Fix: migrar a Tailwind.

2. **Bootstrap clases sin Bootstrap en templates AR** — Archivos: `ar/caza_objetos.html`, `ar/respiracion.html`, `ar/secuencia_luces.html`. Las clases `btn`, `col-*`, `row`, `display-1` no renderizan correctamente. Fix: migrar a Tailwind o cargar Bootstrap en esos templates.

3. **print() excesivo en producción — contamina logs** — Archivos: principalmente `vision/routes.py` (imprime en cada frame procesado). Durante un test de 30 segundos a 30fps = 900 prints. Fix: cambiar a `logging.debug()`.

4. **Botón "Generar análisis con IA" sin feedback de error visible** — Archivo: `app/templates/teacher/create_report.html`. Cuando la API key falta, el endpoint devuelve JSON de error pero el frontend no muestra mensaje al usuario — el botón parece "no funcionar". Fix: manejar respuesta de error en el JS del template.

5. **Trail Making: template existe pero ruta no registrada** — Archivo: `app/ar/routes.py` (falta ruta), `app/templates/ar/trail_making.html`. Si alguien accede a `/ar/trail-making` da 404 y el template es inutilizable. Fix: registrar ruta o eliminar el template.

6. **Session state de visión en memoria (no persiste hot-reload)** — Archivo: `app/assessments/vision/routes.py:30`. A diferencia de Stroop/GoNoGo/Audio que usan `ActiveTestSession` en BD, visión usa un dict en memoria. En desarrollo con `FLASK_DEBUG=True` el auto-reloader borra el estado. Fix: migrar a `ActiveTestSession` similar a Stroop.

7. **Comentario incorrecto en audio/routes.py** — Archivo: `app/assessments/audio/routes.py:275`. Dice "El campo 'age' no existe en el modelo actual" pero sí existe en `Student`. Fix: eliminar o corregir el comentario.

8. **Tablas `parents` y `parent_student` todavía en el esquema** — Archivos: `app/core/models/parent.py`, `app/__init__.py`. Se importan y crean en BD aunque no se usen. Confusión para quien lea el código. Fix: eliminar importación en `__init__.py` y mover `parent.py` a legacy.

### MENORES (cosmético, no urgente)

1. `User.query.get_or_404()` deprecated — `app/admin/routes.py:151,208`. Reemplazar por `db.session.get(User, id) or abort(404)`.

2. ENUM `role` incluye `'parent'` en el modelo `User` — `app/core/models/user.py:13`. Debería ser solo `('admin', 'teacher', 'student')`.

3. Inconsistencia de imports (`app.models.*` vs `app.core.models.*`) — varios archivos. Funcionan igual (re-exports) pero confunde.

4. Texto `text-xs` (12px) en topbar labels — menor accesibilidad para niños.

5. Empty states en `teacher/reports` y `teacher/activities` sin ilustración — tables vacías cuando no hay datos.

6. `.gitignore` no incluye `venv/` (solo `venv/`) — existe una carpeta llamada exactamente `venv` (no `.venv`) y otra `.venv`. El `.gitignore` tiene `venv/` que cubre el `venv` real pero la carpeta visible en el root es `venv` sin punto — correcto.

7. `package-lock.json` en `.gitignore` — el archivo `package-lock.json` debería estar en el repo para reproducibilidad de Tailwind, pero está ignorado.

---

## Recomendación de orden de fix

1. **Agregar matplotlib a requirements.txt** — 5 minutos, sin tocar código. Crítico para que el test de visión funcione en cualquier entorno.

2. **Crear layout AR full-screen** — Crear `ar_layout.html` sin sidebar y hacer que los 3 templates de AR activos lo extiendan. Resuelve el bug visual más grave que hace creer que "no hace nada".

3. **Eliminar 'parent' del dict `role_redirects` en auth.dashboard** — 2 líneas de código. Previene crash si hay usuario con rol parent en BD.

4. **Agregar Stroop y Go/No-Go a `/student/progreso`** — Expande el código de `progress()` para incluir los 4 tipos de test. Fundamental para mostrar trabajo de tesis completo.

5. **Quitar o simplificar prints de debug** — Cambiar los prints masivos de visión a `logging.debug()`. Mejora la experiencia de demo en vivo.

6. **Migrar ar/index.html a Tailwind** — Eliminar el único template de AR que el estudiante ve primero. Quiebre visual muy notorio.

7. **Manejar error de IA en frontend de profesor** — Agregar manejo JS del error `{'error': ...}` en el botón de análisis IA.

8. **Migrar estado de visión a ActiveTestSession** — Mismo patrón que Stroop/GoNoGo. Evita perder tests durante desarrollo.

---

## Anexo: Rutas registradas vs. sidebars

### Admin (4 en sidebar, 9 total registradas)

| Endpoint | URL | En sidebar |
|----------|-----|-----------|
| `admin.index` | `/admin/` | ✅ Dashboard |
| `admin.users` | `/admin/users` | ✅ Usuarios |
| `admin.create_user` | `/admin/users/create` | — (botón en users) |
| `admin.edit_user` | `/admin/users/<id>/edit` | — (tabla de users) |
| `admin.delete_user` | `/admin/users/<id>/delete` POST | — (formulario en edit) |
| `admin.assignments` | `/admin/assignments` | ✅ Asignaciones |
| `admin.assign_student` | `/admin/assignments/assign` POST | — |
| `admin.reports` | `/admin/reports` | ✅ Estadísticas |
| `admin.inscribir_alumno` | `/admin/inscribir-alumno` | — (botón en users) |
| `admin.api_stats` | `/admin/api/stats` | — (API interna) |

### Teacher (4 en sidebar, 9 total registradas)

| Endpoint | URL | En sidebar |
|----------|-----|-----------|
| `teacher.index` | `/teacher/` | ✅ Inicio |
| `teacher.students` | `/teacher/students` | ✅ Estudiantes |
| `teacher.student_detail` | `/teacher/students/<id>` | — |
| `teacher.activities` | `/teacher/activities` | ✅ Actividades |
| `teacher.create_activity` | `/teacher/activities/create` | — (botón topbar) |
| `teacher.generate_activity` | `/teacher/activities/generate` POST | — |
| `teacher.reports` | `/teacher/reports` | ✅ Reportes |
| `teacher.create_report` | `/teacher/reports/create/<session_id>` | — |
| `teacher.report_pdf` | `/teacher/reports/<id>/pdf` | — |
| `teacher.report_send_whatsapp` | `/teacher/reports/<id>/send-whatsapp` POST | — |
| `teacher.session_detail` | `/teacher/sessions/<id>` | — |
| `teacher.ai_suggestions` | `/teacher/api/ai-suggestions` POST | — |

### Student (5 en sidebar, 10 total registradas)

| Endpoint | URL | En sidebar |
|----------|-----|-----------|
| `student.index` | `/student/` | ✅ Inicio |
| `student.tests_index` | `/student/tests` | ✅ Mis Tests |
| `student.activities` | `/student/activities` | ✅ Mis Actividades |
| `student.activity_detail` | `/student/activities/<id>` | — |
| `student.start_activity` | `/student/activities/<id>/start` | — |
| `student.record_session` | `/student/sessions/record` POST | — |
| `student.session_detail` | `/student/sessions/<id>` | — |
| `student.progress` | `/student/progress` | ✅ Mi Progreso |
| `student.progress_export` | `/student/progress/export` | — |
| `student.feedback` | `/student/feedback` | — |
| `ar.index` | `/ar/` | ✅ Actividades AR |

### Tests cognitivos (sin sidebar propio)

| Endpoint | URL | Acceso desde |
|----------|-----|-------------|
| `vision.index` | `/vision/` | student.tests_index |
| `vision.start_test` | `/vision/start_test` POST | |
| `vision.process_frame` | `/vision/process_frame` POST | |
| `vision.finish_test` | `/vision/finish_test/<id>` POST | |
| `vision.results` | `/vision/results` | |
| `audio.index` | `/audio/` | student.tests_index |
| `audio.start_test` | `/audio/start_test` POST | |
| `audio.upload_audio` | `/audio/upload_audio` POST | |
| `audio.results` | `/audio/results` | |
| `stroop.index` | `/stroop/` | student.tests_index |
| `stroop.start_test` | `/stroop/start_test` POST | |
| `stroop.submit_trial` | `/stroop/submit_trial` POST | |
| `stroop.finish_test` | `/stroop/finish_test` POST | |
| `stroop.results` | `/stroop/results` | |
| `gonogo.index` | `/gonogo/` | student.tests_index |
| `gonogo.start_test` | `/gonogo/start_test` POST | |
| `gonogo.submit_trial` | `/gonogo/submit_trial` POST | |
| `gonogo.finish_test` | `/gonogo/finish_test` POST | |
| `gonogo.results` | `/gonogo/results` | |

### AR (sin sidebar propio, acceso desde ar.index)

| Endpoint | URL | En ar/index.html |
|----------|-----|-----------------|
| `ar.index` | `/ar/` | — |
| `ar.caza_objetos` | `/ar/caza-objetos` | ✅ |
| `ar.secuencia_luces` | `/ar/secuencia-luces` | ✅ |
| `ar.respiracion` | `/ar/respiracion` | ✅ |
| `ar.save_result` | `/ar/save-result` POST | — |
| **Trail Making** | **sin ruta** | ❌ template huérfano |

---

## Anexo: Análisis AR — causa raíz de "no hace nada"

### Flujo de carga actual (problemático)

```
Usuario → /ar/caza-objetos
  └─ Renderiza ar/caza_objetos.html
       └─ {% extends 'base.html' %}
            ├─ <aside> sidebar Tailwind (ancho 56px–224px)
            ├─ <div class="flex-1 flex flex-col"> content area
            │    └─ {% block content %}
            │         ├─ <div id="instructions"> instrucciones visibles ✅
            │         ├─ <div id="ui-overlay" style="display:none">
            │         └─ <a-scene style="display:none" embedded>
            └─ A-Frame JS carga ✅
```

**Problema:** Cuando `startGame()` ejecuta:
```javascript
document.getElementById('ar-scene').style.display = 'block';
```
La `<a-scene>` se muestra, pero está dentro del `flex-1 flex flex-col` del layout principal que tiene `overflow: hidden`. El canvas de A-Frame, al ser `embedded`, intenta ajustarse al contenedor padre — pero ese contenedor tiene altura determinada por el layout flex y puede ser 0 o reducido según la altura disponible tras descontar el topbar (56px) y el body padding.

**Por qué parece "en blanco":** La `<a-scene>` renderiza pero con dimensiones incorrectas, o el cielo `<a-sky color="#87CEEB">` se renderiza en un área tan pequeña que no se ve. Los objetos 3D pueden estar renderizándose fuera del viewport visible.

**Solución directa:** Cambiar los templates AR para que extiendan un layout que no tenga sidebar ni topbar:
```html
{# en caza_objetos.html #}
<!DOCTYPE html>
<html>
<head>...</head>
<body style="margin:0; overflow:hidden">
  ...
</body>
</html>
```
O crear `ar_layout.html` con body full-screen y usarlo como base.

**Verificación secundaria:** La consola del navegador probablemente muestra A-Frame inicializando correctamente (sin errores JS), pero la escena renderizada queda oculta o con 0px de alto — confirmando que el problema es de layout, no de A-Frame.
