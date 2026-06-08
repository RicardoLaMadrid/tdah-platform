# Credenciales Demo — Defensa de Tesis

> Generado automáticamente por `scripts/seed_demo.py`
> Fecha: 2026-06-04 12:33

## Colegio
**Unidad Educativa San Martín de Porres** — Cochabamba, Bolivia

---

## Usuarios del sistema

| Rol | Usuario | Contraseña | Email |
|-----|---------|-----------|-------|
| Admin | `admin` | `admin123` | admin@sanmartin.edu.bo |
| Docente | `prof_maria` | `prof123` | m.quispe@sanmartin.edu.bo |
| Docente | `prof_carlos` | `prof123` | c.mamani@sanmartin.edu.bo |

---

## Alumnos

| Alumno | Usuario | Contraseña | Tipo TDAH | Grado | Docente |
|--------|---------|-----------|-----------|-------|---------|
| Sofía Quispe Rojas | `sofia.quispe` | `estudiante123` | Típico (sin TDAH) | 4to Primaria A | prof_maria |
| Mateo Mamani López | `mateo.mamani` | `estudiante123` | Típico (sin TDAH) | 5to Primaria B | prof_maria |
| Valeria Choque Aguilar | `valeria.choque` | `estudiante123` | Inatento | 4to Primaria A | prof_maria |
| Diego Condori Flores | `diego.condori` | `estudiante123` | Inatento | 4to Primaria B | prof_maria |
| Camila Ticona Pérez | `camila.ticona` | `estudiante123` | Hiperactivo | 3ro Primaria A | prof_carlos |
| Sebastián Apaza Núñez | `sebastian.apaza` | `estudiante123` | Hiperactivo | 5to Primaria B | prof_carlos |
| Isabella Villca Cruz | `isabella.villca` | `estudiante123` | Combinado | 4to Primaria A | prof_carlos |
| Joaquín Calle Quiroga | `joaquin.calle` | `estudiante123` | Combinado | 6to Primaria B | prof_carlos |

---

## Estadísticas de datos generados

- **Sofía Quispe Rojas** (typical, confianza 85%): 3 tests, 2 reportes docente, 6 sesiones AR, 2 notifs
- **Mateo Mamani López** (typical, confianza 86%): 3 tests, 2 reportes docente, 4 sesiones AR, 3 notifs
- **Valeria Choque Aguilar** (inatento, confianza 72%): 3 tests, 2 reportes docente, 6 sesiones AR, 2 notifs
- **Diego Condori Flores** (inatento, confianza 64%): 6 tests, 2 reportes docente, 5 sesiones AR, 3 notifs
- **Camila Ticona Pérez** (hiperactivo, confianza 66%): 5 tests, 2 reportes docente, 4 sesiones AR, 3 notifs
- **Sebastián Apaza Núñez** (hiperactivo, confianza 62%): 6 tests, 2 reportes docente, 5 sesiones AR, 3 notifs
- **Isabella Villca Cruz** (combinado, confianza 71%): 4 tests, 2 reportes docente, 4 sesiones AR, 3 notifs
- **Joaquín Calle Quiroga** (combinado, confianza 73%): 5 tests, 2 reportes docente, 5 sesiones AR, 3 notifs

---

## Guía rápida para la defensa

### Demostrar cada tipo de TDAH
- **Sin TDAH (típico):** login con `sofia.quispe` o `mateo.mamani`
- **TDAH Inatento:** login con `valeria.choque` o `diego.condori`
- **TDAH Hiperactivo:** login con `camila.ticona` o `sebastian.apaza`
- **TDAH Combinado:** login con `isabella.villca` o `joaquin.calle`

### Flujo recomendado para demo
1. Login como `admin/admin123` → ver dashboard con métricas globales
2. Inscribir alumno nuevo (wizard 3 pasos)
3. Login como `prof_maria/prof123` → ver grid de alumnos
4. Click en Valeria Choque → ver tabs de progreso, tests, actividades AR
5. Crear reporte con asistencia IA
6. Login como `valeria.choque/estudiante123` → ver dashboard personal

---
*Generado por `scripts/seed_demo.py` — no editar manualmente*