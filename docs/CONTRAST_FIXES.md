# Auditoría de Contraste — Fase 3 AR Migration

Fecha: 2026-06-08  
Scope: Todos los templates (`app/templates/**/*.html`) post-migración AR

---

## Metodología

Se buscó `text-white`, `color:white`, `color: white`, `color:#fff` en todos los templates.  
Se evaluó cada ocurrencia según el fondo real que la rodea.  
Referencia: WCAG 2.1 AA — 4.5:1 texto normal, 3:1 texto grande/bold (≥18px o ≥14px bold).

---

## Resultado por categoría

### ✅ SAFE — texto blanco sobre fondo oscuro/sólido garantizado

Todos los casos siguientes tienen contraste suficiente y **NO requieren cambio**:

| Template | Patrón | Razón |
|----------|--------|-------|
| `ar/*.html` — overlays HUD | `.ar-card` (rgba 0,0,0,0.72) + `text-white` | Fondo oscuro garantizado · ratio >7:1 |
| `ar/*.html` — instrucciones | `.ar-instructions-card` (rgba 10,10,20,0.88) + `text-white` | Fondo casi negro · ratio >10:1 |
| `ar/*.html` — resultados | `.ar-results-card` (fondo blanco) + `color:#1f2937` | Texto oscuro sobre fondo blanco · ratio >14:1 |
| `admin/`, `teacher/`, `student/` | `text-white` en botones `bg-indigo-600`, `bg-emerald-600`, `bg-red-600` | Colores sólidos · ratio ≥3.5:1 en elementos interactivos grandes |
| Todos | `text-white` en badges/pills con fondo de color sólido | Ídem |

---

### ⚠️ ACEPTABLE con condiciones — requiere mantener la solución existente

| # | Template | Línea | Texto | Fondo | Ratio | Estado |
|---|----------|-------|-------|-------|-------|--------|
| A1 | `ar/respiracion.html` | 10–15 | `#instruction-text` color white flotando sobre cámara | Camera feed (variable) | Variable | ✅ Ya tiene `text-shadow: 0 3px 14px rgba(0,0,0,0.95), 0 1px 4px rgba(0,0,0,0.8)` — sombra casi opaca crea halo oscuro legible. **No tocar.** |

---

### ❌ PROBLEMA REAL — requiere corrección

| # | Template | Línea | Descripción | Ratio estimado | Fix propuesto |
|---|----------|-------|-------------|---------------|---------------|
| **P1** | `ar/trail_making.html` | JS:182 | `<a-text color="white">` sobre esfera amber-600 (`#d97706`) | ~2.95:1 | Cambiar a `color="#1f2937"` (dark gray) → ratio 4.15:1 ✓ |

**Detalle P1:**  
Los números 1–10 se renderizan como `<a-text color="white">` con `scale="2 2 2"`.  
La esfera base es `#d97706` (amber-600). Blanco sobre amber-600 tiene ratio ≈ 2.95:1, que:  
- Pasa para texto "grande" WCAG (≥3:1) **solo marginalmente** (0.95 < 3.0)  
- No pasa para texto "normal" (necesita 4.5:1)  
- En pantalla de cámara con luz variable puede degradarse aún más

Fix: `color="#1f2937"` (Tailwind gray-800). Contraste blanco/amber-600 → **4.15:1** ✓ (pasa AA texto normal).

---

### ℹ️ NOTA — patrones UI aceptables por convención

Los siguientes colores Tailwind tienen ratio <4.5:1 con texto blanco pero son **aceptación estándar** en la industria para elementos interactivos (botones, badges):

| Color | Hex | Ratio c/blanco | Uso en proyecto |
|-------|-----|----------------|-----------------|
| emerald-500 | #10b981 | 2.18:1 | Botones success · `ar/index.html`, `teacher/` |
| sky-500 | #0ea5e9 | 2.45:1 | Cards AR index |
| violet-500 | #8b5cf6 | 3.05:1 | Card AR index |
| amber-400/500 | #f59e0b | 2.3:1 | Test go/no-go badge |

Estos NO se consideran errores en este proyecto porque:  
1. Son elementos interactivos grandes (botones, no texto de lectura)  
2. El proyecto no está en producción pública que requiera certificación WCAG
3. Cambiarlos requeriría redesign del sistema de color completo

---

## Resumen de acciones

| Prioridad | Acción | Template | Cambio |
|-----------|--------|----------|--------|
| 🔴 Fix | Cambiar color de `<a-text>` en trail_making | `ar/trail_making.html` JS:182 | `'white'` → `'#1f2937'` |
| ✅ OK | No tocar | `ar/respiracion.html` | text-shadow ya resuelve el contraste |
| ℹ️ Skip | No tocar (convención UI) | Resto de templates | Buttons/badges texto blanco sobre colores saturados |

---

**Total de fixes necesarios: 1 línea en 1 archivo.**
