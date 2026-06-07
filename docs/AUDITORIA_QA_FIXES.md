# Auditoría QA — Corrección de Bugs Pre-Defensa

**Fecha:** 2026-06-07  
**Branch:** `refactor-v2`  
**Autor:** Ricardo La Madrid

---

## Resumen Ejecutivo

Se corrigieron 5 bugs críticos identificados en la auditoría QA pre-defensa. El servidor arranca sin errores ni warnings. Se migró completamente Bootstrap → Tailwind CSS en todos los templates.

---

## Bug #1 — matplotlib faltante en requirements.txt

**Severidad:** Alta (bloquea despliegue en entorno limpio)  
**Archivos afectados:** `requirements.txt`

**Problema:** `matplotlib` se usaba en `app/blueprints/teacher/routes.py` para generar gráficos, pero no estaba declarado en `requirements.txt`. Un `pip install -r requirements.txt` en entorno limpio generaba `ImportError`.

**Solución:** Se agregó `matplotlib==3.9.4` a `requirements.txt`.

**Commit:** `feat(deps): agregar matplotlib a requirements.txt`

---

## Bug #2 — AR templates aplastados por el sidebar

**Severidad:** Alta (rompe la experiencia de usuario en actividades AR)  
**Archivos afectados:** `app/shared/templates/base.html`, `app/templates/ar/*.html`

**Problema:** Las plantillas AR usaban `{% block page_mode %}ar{% endblock %}` para señalizar modo fullscreen, pero `base.html` no tenía ningún bloque `page_mode` definido ni lógica para ocultarlo del sidebar. Los templates AR se renderizaban dentro del layout con sidebar, comprimiendo el canvas de A-Frame.

**Solución:** Se agregó `{% block page_mode %}normal{% endblock %}` en `base.html`. Se captura con `{% set _fs = self.page_mode() == 'ar' %}` y se bifurca el layout: si `_fs` es verdadero, solo se renderiza un `<main class="w-screen h-screen overflow-hidden">` sin sidebar ni navbar.

**Fix colateral:** Al hacer esta corrección se detectó que la rama `{% if _fs %}` tenía `{% block content %}{% endblock %}`, causando "block content defined twice". Se corrigió usando `{{ self.content() }}` en la rama AR.

**Commit:** `fix(base): layout AR fullscreen — ocultar sidebar en page_mode=ar`  
**Commit:** `fix(base): corregir 'block content defined twice' usando self.content() en rama AR`

---

## Bug #3 — Rol 'parent' residual en el código

**Severidad:** Media (puede causar errores en rutas de administración)  
**Archivos afectados:** `app/blueprints/admin/routes.py`, `app/models/`, scripts SQL

**Problema:** El rol 'parent' fue eliminado del negocio pero quedaron referencias en el código: rutas de admin que asumían que `ParentProfile` existía, lógica de asignación de vínculos padre-hijo, y registros en la base de datos.

**Solución:** Se eliminaron rutas y lógica de 'parent' del blueprint de admin. Se creó `scripts/migrations/remove_parent_role.sql` para limpiar la base de datos.

**Acción manual requerida:** Ejecutar `scripts/migrations/remove_parent_role.sql` en phpMyAdmin antes de la defensa.

**Commit:** `fix(admin): eliminar rol parent residual del código`

---

## Bug #4 — Progreso del estudiante incompleto

**Severidad:** Alta (pantalla de progreso mostraba solo actividades, sin tests cognitivos)  
**Archivos afectados:** `app/blueprints/student/routes.py`, `app/templates/student/progress.html`

**Problema:** La ruta `/student/progress` solo consultaba `ActivitySession`. Los tests cognitivos (Visión, Audio, Stroop, Go/No-Go) guardaban resultados en tablas separadas (`VisionTestSession`, `AudioTestSession`, etc.) y no aparecían en el timeline de progreso del estudiante.

**Solución:** Se modificó la ruta para consultar todas las tablas de sesiones de tests, unificar en una lista cronológica, y calcular estadísticas globales. Se rediseñó el template `progress.html` para mostrar el timeline unificado con todos los tipos de actividad.

**Commit:** `feat(student): progreso completo con todos los tipos de tests y actividades`

---

## Bug #5 — Bootstrap residual en 22+ templates

**Severidad:** Alta (Bootstrap no está cargado en base.html Tailwind; clases sin efecto visual)  
**Fase:** 5.1 grep/map → 5.2 categorizar → 5.3 migrar → 5.4 verificar

### Templates migrados (Bootstrap → Tailwind)

| Template | Cambios principales |
|---|---|
| `ar/index.html` | Grid de cards, stat cards, info box |
| `ar/caza_objetos.html` | btn, display-1, row/col, alert, lead |
| `ar/respiracion.html` | btn, display-1, row/col, alert-info, lead |
| `ar/secuencia_luces.html` | btn, display-1, row/col, lead |
| `ar/trail_making.html` | btn, text-success/danger, text-muted, lead, row/col, alert |
| `student/progress.html` | container-fluid, row, col-*, card, timeline list-group, extra CSS Bootstrap |
| `student/activities.html` | Card grid, badge absolute, progress bar, d-grid btn |
| `student/activity_detail.html` | card, card-header, list-group, badge bg-*, d-flex, d-grid |
| `student/session_detail.html` | container, row, col-*, card, card-header, score-display, list-unstyled, img-fluid |
| `student/feedback.html` | container-fluid, row, col-md-6, card, card-header, badge bg-info, d-flex |
| `student/activity_player.html` | btn btn-*, alert alert-info; custom CSS preservado |
| `teacher/students.html` | Card grid, user-avatar, progress bar |
| `teacher/reports.html` | col-md-6, card, card-header, card-footer |
| `teacher/session_detail.html` | container-fluid, row, col-md-4/8, card, progress, list-group, score-display |
| `teacher/create_activity.html` | Bootstrap modal → Alpine.js modal, form-select, form-check, spinner-border |
| `admin/assignments.html` | Bootstrap modals → Alpine.js (`x-data`, `x-show`, `x-cloak`), tabla |
| `admin/reports.html` | stat-card custom CSS → Tailwind colored divs, table-hover, progress bar |
| `admin/edit_user.html` | Formulario complejo con macro Jinja2, cmap Bootstrap→Tailwind |
| `admin/parent_links.html` | form-select, table-hover, badge bg-secondary, btn btn-sm btn-danger |
| `auth/register.html` | container, row, col-md-6, card, card-body |
| `auth/profile.html` | card, avatar form |
| `errors/404.html` | Página centrada simple |
| `errors/500.html` | Página centrada simple |

### Patrones de migración establecidos

**Alpine.js modal** (reemplaza Bootstrap `data-bs-toggle="modal"`):
```html
<div x-data="{ openModal: null }">
  <button @click="openModal = id">...</button>
  <div x-show="openModal === id" x-cloak class="fixed inset-0 z-50 ...">
    <div @click="openModal = null" class="absolute inset-0 bg-black/50"></div>
    <div class="relative bg-white rounded-2xl ...">...</div>
  </div>
</div>
```

**Alpine.js toggle switch** (reemplaza Bootstrap form-switch):
```html
<input type="checkbox" x-model="arEnabled" class="sr-only">
<div class="w-10 h-5 rounded-full transition-colors"
     :class="arEnabled ? 'bg-emerald-500' : 'bg-slate-300'"></div>
<div class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
     :class="arEnabled ? 'translate-x-5' : 'translate-x-0'"></div>
```

**Bootstrap color mapping** para valores de `get_confianza_color()`:
```jinja2
{%- set cmap = {'success':'bg-emerald-100 text-emerald-700','warning':'bg-amber-100 text-amber-700',
                'danger':'bg-red-100 text-red-700','info':'bg-sky-100 text-sky-700'} -%}
```

### Verificación Phase 5.4

```
grep -rl "data-bs-toggle|card-body|col-md-|btn btn-|list-group|form-control|d-flex" app/templates/ --include="*.html"
```

**Resultado:** Solo `base_bootstrap_legacy.html` (archivo sin referencias, no usado por ninguna ruta).

**Commits de migración:** 10 commits `refactor(template): migrar ... de Bootstrap a Tailwind`

---

## Estado del servidor

```
python run.py
✅ Google OAuth configurado
============================================================
APLICACION INICIALIZADA CORRECTAMENTE
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Sin warnings de importación, sin errores de template, sin errores de base de datos.

---

## Hallazgos colaterales (no corregidos — fuera de alcance)

1. `base_bootstrap_legacy.html` — archivo huérfano sin referencias. Puede eliminarse.
2. `scripts/migrations/remove_parent_role.sql` — requiere ejecución manual en phpMyAdmin.
3. `teacher/student_detail.html` y `teacher/create_report.html` — inicialmente en lista Bootstrap, pero verificados como ya migrados (false positives del grep).

---

*Documento generado post-corrección de bugs pre-defensa*
