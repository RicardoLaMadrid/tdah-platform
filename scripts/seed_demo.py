#!/usr/bin/env python3
"""
scripts/seed_demo.py — Datos demo para defensa de tesis TDAH Platform
Uso:
  python scripts/seed_demo.py           # Agrega datos si no existen
  python scripts/seed_demo.py --reset   # Borra todo y recrea desde cero
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

try:
    from faker import Faker
    fake = Faker(["es_MX"])
except ImportError:
    print("ERROR: Faker no está instalado. Ejecuta: pip install Faker")
    sys.exit(1)

random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# DATOS FIJOS
# ─────────────────────────────────────────────────────────────────────────────

USERS_FIXED = [
    {
        "username": "admin",
        "email": "admin@sanmartin.edu.bo",
        "password": "admin123",
        "role": "admin",
    },
    {
        "username": "prof_maria",
        "email": "m.quispe@sanmartin.edu.bo",
        "password": "prof123",
        "role": "teacher",
    },
    {
        "username": "prof_carlos",
        "email": "c.mamani@sanmartin.edu.bo",
        "password": "prof123",
        "role": "teacher",
    },
]

STUDENTS_DATA = [
    # ── TYPICAL ───────────────────────────────────────────────────────────────
    {
        "full_name": "Sofía Quispe Rojas",
        "username": "sofia.quispe",
        "email": "sofia.quispe@sanmartin.edu.bo",
        "password": "estudiante123",
        "age": 10,
        "grade": "4to Primaria",
        "section": "A",
        "national_id": "7845123",
        "tdah_type": "typical",
        "teacher_username": "prof_maria",
        "address": "Av. Heroínas #456, Zona Cala Cala, Cochabamba",
        "emergency_contact_name": "Ana María Quispe Mamani",
        "emergency_contact_phone": "+591 72345678",
        "tutor_full_name": "Luis Quispe Mamani",
        "tutor_relationship": "padre",
        "tutor_phone": "+591 71234567",
        "tutor_email": "luis.quispe@gmail.com",
        "tutor_national_id": "4523187",
        "allergies": None,
        "medical_conditions": None,
        "medications": None,
        "notes": "Alumna destacada, excelente participación en clase.",
    },
    {
        "full_name": "Mateo Mamani López",
        "username": "mateo.mamani",
        "email": "mateo.mamani@sanmartin.edu.bo",
        "password": "estudiante123",
        "age": 11,
        "grade": "5to Primaria",
        "section": "B",
        "national_id": "8234567",
        "tdah_type": "typical",
        "teacher_username": "prof_maria",
        "address": "Calle Sucre #123, Zona La Recoleta, Cochabamba",
        "emergency_contact_name": "Carmen López Vargas",
        "emergency_contact_phone": "+591 76543210",
        "tutor_full_name": "Juan Mamani Quispe",
        "tutor_relationship": "padre",
        "tutor_phone": "+591 77654321",
        "tutor_email": "j.mamani@gmail.com",
        "tutor_national_id": "3812456",
        "allergies": "Polen, polvo",
        "medical_conditions": None,
        "medications": "Antihistamínico (según indicación médica)",
        "notes": "Buen rendimiento académico general.",
    },
    # ── INATENTO ──────────────────────────────────────────────────────────────
    {
        "full_name": "Valeria Choque Aguilar",
        "username": "valeria.choque",
        "email": "valeria.choque@sanmartin.edu.bo",
        "password": "estudiante123",
        "age": 9,
        "grade": "4to Primaria",
        "section": "A",
        "national_id": "7123456",
        "tdah_type": "inatento",
        "teacher_username": "prof_maria",
        "address": "Av. Blanco Galindo Km 5, Zona Sacaba, Cochabamba",
        "emergency_contact_name": "Rosa Aguilar de Choque",
        "emergency_contact_phone": "+591 71239876",
        "tutor_full_name": "Roberto Choque Flores",
        "tutor_relationship": "padre",
        "tutor_phone": "+591 72345987",
        "tutor_email": "r.choque.familia@gmail.com",
        "tutor_national_id": "5672341",
        "allergies": None,
        "medical_conditions": "TDAH tipo inatento (diagnóstico previo neurología)",
        "medications": "Metilfenidato 5mg (mañana, según prescripción)",
        "notes": "Requiere recordatorios frecuentes para retomar tareas.",
    },
    {
        "full_name": "Diego Condori Flores",
        "username": "diego.condori",
        "email": "diego.condori@sanmartin.edu.bo",
        "password": "estudiante123",
        "age": 10,
        "grade": "4to Primaria",
        "section": "B",
        "national_id": "7654321",
        "tdah_type": "inatento",
        "teacher_username": "prof_maria",
        "address": "Calle España #78, Zona Tiquipaya, Cochabamba",
        "emergency_contact_name": "María Flores Condori",
        "emergency_contact_phone": "+591 71876543",
        "tutor_full_name": "Pedro Condori Mamani",
        "tutor_relationship": "padre",
        "tutor_phone": "+591 71987654",
        "tutor_email": "condori.pedro@hotmail.com",
        "tutor_national_id": "4789123",
        "allergies": "Penicilina",
        "medical_conditions": None,
        "medications": None,
        "notes": "Olvida frecuentemente el material escolar. Mejoró con agenda visual.",
    },
    # ── HIPERACTIVO ───────────────────────────────────────────────────────────
    {
        "full_name": "Camila Ticona Pérez",
        "username": "camila.ticona",
        "email": "camila.ticona@sanmartin.edu.bo",
        "password": "estudiante123",
        "age": 9,
        "grade": "3ro Primaria",
        "section": "A",
        "national_id": "7321654",
        "tdah_type": "hiperactivo",
        "teacher_username": "prof_carlos",
        "address": "Av. Ayacucho #234, Zona Quillacollo, Cochabamba",
        "emergency_contact_name": "Elena Pérez de Ticona",
        "emergency_contact_phone": "+591 72109876",
        "tutor_full_name": "Hugo Ticona Vargas",
        "tutor_relationship": "padre",
        "tutor_phone": "+591 71234098",
        "tutor_email": "hugo.ticona@gmail.com",
        "tutor_national_id": "3456789",
        "allergies": None,
        "medical_conditions": "TDAH tipo hiperactivo-impulsivo",
        "medications": None,
        "notes": "Muy activa, responde bien a estímulos visuales y movimiento.",
    },
    {
        "full_name": "Sebastián Apaza Núñez",
        "username": "sebastian.apaza",
        "email": "sebastian.apaza@sanmartin.edu.bo",
        "password": "estudiante123",
        "age": 11,
        "grade": "5to Primaria",
        "section": "B",
        "national_id": "8765432",
        "tdah_type": "hiperactivo",
        "teacher_username": "prof_carlos",
        "address": "Calle Aroma #567, Zona Sacaba, Cochabamba",
        "emergency_contact_name": "Patricia Núñez Apaza",
        "emergency_contact_phone": "+591 77234561",
        "tutor_full_name": "César Apaza Chura",
        "tutor_relationship": "padre",
        "tutor_phone": "+591 76345672",
        "tutor_email": "c.apaza@yahoo.com",
        "tutor_national_id": "5234678",
        "allergies": None,
        "medical_conditions": None,
        "medications": None,
        "notes": "Le cuesta mantenerse sentado. Mejora con pausas activas cada 20 min.",
    },
    # ── COMBINADO ─────────────────────────────────────────────────────────────
    {
        "full_name": "Isabella Villca Cruz",
        "username": "isabella.villca",
        "email": "isabella.villca@sanmartin.edu.bo",
        "password": "estudiante123",
        "age": 10,
        "grade": "4to Primaria",
        "section": "A",
        "national_id": "7432165",
        "tdah_type": "combinado",
        "teacher_username": "prof_carlos",
        "address": "Av. América #890, Zona Cala Cala, Cochabamba",
        "emergency_contact_name": "Rosa Cruz Villca",
        "emergency_contact_phone": "+591 72876543",
        "tutor_full_name": "Antonio Villca Quispe",
        "tutor_relationship": "padre",
        "tutor_phone": "+591 71987234",
        "tutor_email": "a.villca.familia@gmail.com",
        "tutor_national_id": "4321987",
        "allergies": "Mariscos",
        "medical_conditions": "TDAH tipo combinado",
        "medications": "Metilfenidato 10mg (mañana, según prescripción médica)",
        "notes": "Presenta inatención e impulsividad. Requiere estrategias dobles.",
    },
    {
        "full_name": "Joaquín Calle Quiroga",
        "username": "joaquin.calle",
        "email": "joaquin.calle@sanmartin.edu.bo",
        "password": "estudiante123",
        "age": 12,
        "grade": "6to Primaria",
        "section": "B",
        "national_id": "9123456",
        "tdah_type": "combinado",
        "teacher_username": "prof_carlos",
        "address": "Calle Jordán #321, Zona La Recoleta, Cochabamba",
        "emergency_contact_name": "Lucía Quiroga de Calle",
        "emergency_contact_phone": "+591 71654321",
        "tutor_full_name": "Marco Calle Fernández",
        "tutor_relationship": "padre",
        "tutor_phone": "+591 72765432",
        "tutor_email": "marco.calle@gmail.com",
        "tutor_national_id": "6712345",
        "allergies": None,
        "medical_conditions": None,
        "medications": None,
        "notes": "Mayor del grupo. Liderazgo presente pero impulsivo.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def rand_date(min_days: int, max_days: int) -> datetime:
    days = random.randint(min_days, max_days)
    return datetime.utcnow() - timedelta(
        days=days,
        hours=random.randint(7, 17),
        minutes=random.randint(0, 59),
    )


def jitter(value: float, pct: float = 0.12) -> float:
    delta = abs(value) * pct
    return round(value + random.uniform(-delta, delta), 2)


# Métricas base por tipo TDAH para cada test
_BASE: dict = {
    "vision_test": {
        "typical":     {"confianza": 83, "attention_score_center": 78, "gaze_stability_index": 0.87, "distraction_events": 2,  "fixation_duration_avg_ms": 285, "saccade_frequency": 1.1, "heatmap_coverage": 0.86},
        "inatento":    {"confianza": 70, "attention_score_center": 44, "gaze_stability_index": 0.50, "distraction_events": 9,  "fixation_duration_avg_ms": 172, "saccade_frequency": 2.9, "heatmap_coverage": 0.63},
        "hiperactivo": {"confianza": 68, "attention_score_center": 62, "gaze_stability_index": 0.58, "distraction_events": 6,  "fixation_duration_avg_ms": 210, "saccade_frequency": 2.2, "heatmap_coverage": 0.71},
        "combinado":   {"confianza": 74, "attention_score_center": 38, "gaze_stability_index": 0.44, "distraction_events": 11, "fixation_duration_avg_ms": 158, "saccade_frequency": 3.2, "heatmap_coverage": 0.60},
    },
    "stroop_test": {
        "typical":     {"confianza": 85, "tiempo_reaccion_promedio_ms": 510, "errores": 2,  "interferencia_score": 88, "inhibicion_cognitiva": 91},
        "inatento":    {"confianza": 69, "tiempo_reaccion_promedio_ms": 815, "errores": 4,  "interferencia_score": 55, "inhibicion_cognitiva": 63},
        "hiperactivo": {"confianza": 74, "tiempo_reaccion_promedio_ms": 412, "errores": 9,  "interferencia_score": 50, "inhibicion_cognitiva": 54},
        "combinado":   {"confianza": 75, "tiempo_reaccion_promedio_ms": 705, "errores": 8,  "interferencia_score": 44, "inhibicion_cognitiva": 49},
    },
    "gonogo_test": {
        "typical":     {"confianza": 86, "false_positives": 2,  "misses": 1,  "inhibicion_rate": 0.92, "impulsividad_score": 11},
        "inatento":    {"confianza": 68, "false_positives": 3,  "misses": 8,  "inhibicion_rate": 0.78, "impulsividad_score": 27},
        "hiperactivo": {"confianza": 79, "false_positives": 14, "misses": 1,  "inhibicion_rate": 0.33, "impulsividad_score": 83},
        "combinado":   {"confianza": 75, "false_positives": 10, "misses": 7,  "inhibicion_rate": 0.52, "impulsividad_score": 65},
    },
    "audio_test": {
        "typical":     {"confianza": 81, "comprension_score": 90, "pausas_detectadas": 1, "tiempo_respuesta_promedio_s": 1.9, "precision_transcripcion": 0.93},
        "inatento":    {"confianza": 66, "comprension_score": 53, "pausas_detectadas": 7, "tiempo_respuesta_promedio_s": 5.2, "precision_transcripcion": 0.67},
        "hiperactivo": {"confianza": 63, "comprension_score": 73, "pausas_detectadas": 2, "tiempo_respuesta_promedio_s": 1.4, "precision_transcripcion": 0.81},
        "combinado":   {"confianza": 71, "comprension_score": 49, "pausas_detectadas": 6, "tiempo_respuesta_promedio_s": 4.3, "precision_transcripcion": 0.62},
    },
}

_TEST_NOTES: dict = {
    "vision_test": {
        "typical":     "Seguimiento ocular estable, foco central sostenido.",
        "inatento":    "Dificultad para mantener foco central, mirada dispersa frecuente.",
        "hiperactivo": "Movimientos oculares rápidos y erráticos, frecuentes cambios de foco.",
        "combinado":   "Patrón mixto: mirada errática con episodios de foco breve.",
    },
    "stroop_test": {
        "typical":     "Excelente control inhibitorio y velocidad de respuesta.",
        "inatento":    "Tiempo de respuesta elevado, errores por inatención.",
        "hiperactivo": "Respuestas rápidas pero con alta tasa de errores impulsivos.",
        "combinado":   "Errores por impulsividad combinados con lentitud en bloques sostenidos.",
    },
    "gonogo_test": {
        "typical":     "Correcta inhibición de respuestas en señales No-Go.",
        "inatento":    "Múltiples omisiones en señales Go, déficit atencional evidente.",
        "hiperactivo": "Alto índice de falsos positivos, control inhibitorio deteriorado.",
        "combinado":   "Tanto falsos positivos como omisiones, patrón combinado confirmado.",
    },
    "audio_test": {
        "typical":     "Comprensión auditiva dentro de parámetros normales.",
        "inatento":    "Múltiples pausas y bajo score de comprensión auditiva.",
        "hiperactivo": "Respuestas apresuradas antes de completar el estímulo auditivo.",
        "combinado":   "Comprensión reducida con respuestas prematuras intermitentes.",
    },
}


def make_test_content(tdah_type: str, report_type: str) -> dict:
    metrics = _BASE.get(report_type, {}).get(tdah_type, {})
    if not metrics:
        return {"tipo_tdah": tdah_type, "confianza": 65}

    result: dict = {}
    for k, v in metrics.items():
        result[k] = jitter(v) if isinstance(v, float) else max(1, int(jitter(float(v))))

    result["tipo_tdah"] = tdah_type
    result["confianza"] = max(55, min(95, result.get("confianza", 65)))
    result["notas"] = _TEST_NOTES.get(report_type, {}).get(tdah_type, "")

    if report_type == "vision_test":
        result["duracion_segundos"] = random.randint(90, 150)
    elif report_type == "stroop_test":
        result["total_ensayos"] = 40
        result["respuestas_correctas"] = max(1, 40 - result.get("errores", 3))
    elif report_type == "gonogo_test":
        result["total_go"] = 30
        result["total_nogo"] = 20
        result["hits"] = max(0, 30 - result.get("misses", 1))
        result["correct_rejections"] = max(0, 20 - result.get("false_positives", 2))
    elif report_type == "audio_test":
        result["duracion_segundos"] = random.randint(60, 120)
        result["palabras_totales"] = 50

    return result


# Textos narrativos de reportes del profesor por tipo TDAH
_TEACHER_REPORTS: dict = {
    "typical": [
        (
            "Durante el período evaluado, {name} demostró un desempeño dentro de los parámetros normales esperados para su grupo etario. Muestra buena capacidad de atención sostenida en tareas estructuradas y responde adecuadamente a las instrucciones del aula. Sus actividades en la plataforma digital muestran consistencia y motivación por el aprendizaje. Se observa progreso continuo en todas las áreas evaluadas.",
            "- Continuar con actividades de refuerzo positivo para mantener la motivación\n- Proponer desafíos de mayor complejidad para estimular el desarrollo cognitivo\n- Fomentar hábitos de lectura independiente en casa (20 min/día)\n- Mantener comunicación regular con el tutor sobre el progreso",
        ),
        (
            "En la segunda evaluación, {name} continúa mostrando un desarrollo cognitivo apropiado. Completa las actividades en el tiempo esperado y mantiene la concentración durante las sesiones de trabajo. La comunicación con el tutor ha sido fluida y el apoyo en casa se refleja positivamente en el rendimiento escolar. El alumno demuestra buena disposición hacia las actividades de realidad aumentada.",
            "- Introducir proyectos de investigación guiada para estimular el pensamiento crítico\n- Fomentar la participación en actividades extracurriculares de su interés\n- Revisar periódicamente si el nivel de desafío académico sigue siendo apropiado\n- Mantener el apoyo familiar como factor clave del rendimiento",
        ),
    ],
    "inatento": [
        (
            "Durante el período evaluado, {name} mostró dificultad para mantener la atención en tareas de larga duración, especialmente en lecturas extensas y ejercicios matemáticos de varios pasos. Sin embargo, su comportamiento es tranquilo y respeta las normas del aula. Sus mejores momentos de aprendizaje ocurren en actividades visuales cortas y dinámicas. Los tests cognitivos confirman el patrón de inatención sin componente impulsivo significativo.",
            "- Dividir las tareas largas en bloques de 10-15 minutos con breves descansos\n- Ubicar al alumno cerca del docente para reorientar la atención con señales discretas\n- Usar organizadores visuales (mapas conceptuales, listas de pasos) como apoyo\n- Practicar lectura compartida en casa por 15 minutos diarios con refuerzo verbal",
        ),
        (
            "En el seguimiento de este período, {name} continúa presentando el patrón de inatención documentado. Se ha implementado la estrategia de bloques de tarea cortos con resultado positivo: completa más actividades cuando se dividen en segmentos de 10-15 minutos. Se recomienda mantener esta adaptación y fortalecer la rutina de organización de materiales escolares.",
            "- Mantener la estrategia de bloques cortos de tarea, muestra resultados positivos\n- Revisar con el tutor si el entorno de estudio en casa minimiza distractores\n- Reforzar positivamente cada logro de concentración, por pequeño que sea\n- Considerar evaluación periódica con especialista si los síntomas persisten",
        ),
    ],
    "hiperactivo": [
        (
            "Durante el período evaluado, {name} mostró alto nivel de energía y dinamismo en el aula, lo que en algunas ocasiones interrumpe las actividades grupales. Responde bien a instrucciones directas y precisas. Los tests Go/No-Go evidencian dificultad en el control inhibitorio motoro. Su motivación para las actividades AR es notable y aprovecha bien los momentos de actividad física estructurada.",
            "- Asignar roles activos en el aula (repartidor de materiales, líder de equipo) para canalizar energía\n- Implementar pausas de movimiento de 2-3 minutos cada 20 minutos de trabajo\n- Usar señales visuales discretas para indicar el momento de calmarse\n- Establecer un sistema de puntos para reforzar el autocontrol y la espera de turno",
        ),
        (
            "En el seguimiento, se observa que {name} ha mejorado su autocontrol cuando se le asignan roles activos dentro del aula. Persiste la dificultad para mantenerse sentado en períodos largos, pero las pausas de movimiento implementadas cada 20 minutos han reducido las interrupciones. Se recomienda continuar con esta estrategia y evaluar en 30 días.",
            "- Continuar con las pausas activas y evaluar reducir su frecuencia gradualmente\n- Introducir técnicas de respiración guiada como herramienta de autorregulación\n- Coordinar con el tutor para aplicar las mismas estrategias de control en el hogar\n- Reconocer y celebrar los avances en autocontrol ante el grupo",
        ),
    ],
    "combinado": [
        (
            "Durante el período evaluado, {name} presenta una combinación de síntomas que incluyen inatención e impulsividad. En momentos de alta estimulación tiende a actuar antes de reflexionar, y en tareas de menor estímulo pierde el hilo de trabajo con facilidad. Los tests AR muestran atención fragmentada con episodios de actividad motora elevada. Requiere un enfoque diferenciado que aborde simultáneamente ambas dimensiones.",
            "- Combinar bloques de trabajo cortos (10-15 min) con la técnica pausa-piensa-actúa\n- Proporcionar agenda visual diaria con tiempos claros y predecibles\n- Utilizar zona de trabajo sin distractores visuales en el aula\n- Coordinar con el tutor para reforzar en casa la rutina de tareas estructuradas",
        ),
        (
            "En el seguimiento, se han implementado estrategias combinadas: agenda visual diaria y técnica 'pausa-piensa-actúa' para el control impulsivo. {name} responde positivamente a la agenda cuando es consistente. Los períodos de concentración han aumentado en promedio de 8 a 13 minutos. Se recomienda mantener ambas estrategias y evaluar ajustes en la próxima reunión con el especialista.",
            "- Mantener el doble enfoque (inatención + impulsividad) de manera consistente\n- Introducir pausas de mindfulness breves (2 min) antes de actividades de evaluación\n- Solicitar evaluación periódica con especialista en TDAH para ajuste de estrategias\n- Reconocer y celebrar los progresos en regulación emocional con el tutor",
        ),
    ],
}

_PARENT_COMMENTS: dict = {
    "typical":     "En casa también notamos buena disposición. Cumple con las tareas sin mayor supervisión. Agradecemos el trabajo del docente.",
    "inatento":    "Hemos implementado el horario sugerido. Cuesta un poco pero ya hay mejoras en las tardes. Gracias por el apoyo.",
    "hiperactivo": "Es cierto que tiene mucha energía. Lo anotamos a fútbol los sábados y ha ayudado bastante. Seguimos las recomendaciones.",
    "combinado":   "Usamos la agenda visual como sugirió. Al principio protestó pero ya la respeta. Pendientes de la próxima evaluación.",
}

_AR_ACTIVITIES: list = [
    {
        "title": "Caza de Objetos AR",
        "description": "Encuentra objetos ocultos en el entorno usando realidad aumentada",
        "activity_type": "ar_caza",
        "difficulty_level": 2,
        "instructions": "1. Apunta la cámara al entorno\n2. Busca los objetos destacados\n3. Toca cada objeto al encontrarlo",
        "ar_content": {"enabled": True, "type": "markerless", "objects_count": 5},
    },
    {
        "title": "Secuencia de Colores AR",
        "description": "Memoriza y repite secuencias de colores en espacio 3D",
        "activity_type": "ar_secuencia",
        "difficulty_level": 1,
        "instructions": "1. Observa la secuencia\n2. Memoriza el orden\n3. Toca los objetos en el mismo orden",
        "ar_content": {"enabled": True, "type": "marker", "sequence_length": 4},
    },
    {
        "title": "Respiración con Globo AR",
        "description": "Ejercicio de respiración guiada con retroalimentación visual AR",
        "activity_type": "ar_respiracion",
        "difficulty_level": 1,
        "instructions": "1. Infla el globo virtual respirando profundo\n2. Sigue el ritmo indicado\n3. Completa 5 ciclos",
        "ar_content": {"enabled": True, "type": "face", "cycles": 5},
    },
    {
        "title": "Trail Making AR",
        "description": "Conecta puntos en orden ascendente en el espacio aumentado",
        "activity_type": "ar_trail_making",
        "difficulty_level": 3,
        "instructions": "1. Localiza los puntos numerados\n2. Conectalos del 1 al 10\n3. Sin errores ni saltos",
        "ar_content": {"enabled": True, "type": "markerless", "points": 10},
    },
]

_ATTENTION_SCORES: dict = {
    "typical":     (74, 92),
    "inatento":    (42, 61),
    "hiperactivo": (55, 72),
    "combinado":   (38, 60),
}

_COMPLETION_TIMES: dict = {
    "typical":     (160, 280),
    "inatento":    (260, 400),
    "hiperactivo": (110, 200),
    "combinado":   (200, 360),
}

_NOTIF_TEMPLATES: list = [
    ("new_test_result",    "Resultado de evaluación disponible",   "Se ha procesado un nuevo resultado de evaluación cognitiva para {name}. Ingresa a la plataforma para ver el detalle."),
    ("new_report",         "Nuevo reporte del docente",            "El docente ha generado un nuevo reporte de progreso para {name}. Te recomendamos revisarlo y comunicarte con el colegio."),
    ("achievement_unlocked", "¡Logro desbloqueado!",              "{name} completó exitosamente una actividad de realidad aumentada. ¡Felicitaciones por el esfuerzo!"),
]


# ─────────────────────────────────────────────────────────────────────────────
# RESET
# ─────────────────────────────────────────────────────────────────────────────

def reset_database(db, models: dict) -> None:
    print("\n  Eliminando datos existentes (respeta el esquema)...")
    Notification = models["Notification"]
    Report = models["Report"]
    Session = models["Session"]
    Activity = models["Activity"]
    Student = models["Student"]
    User = models["User"]

    db.session.query(Notification).delete()
    db.session.query(Report).delete()
    db.session.query(Session).delete()
    db.session.query(Activity).delete()
    db.session.query(Student).delete()
    db.session.query(User).delete()
    db.session.commit()
    print("  Base de datos limpiada.")


# ─────────────────────────────────────────────────────────────────────────────
# SEED
# ─────────────────────────────────────────────────────────────────────────────

def seed_users(db, User) -> dict:
    """Crea usuarios fijos. Retorna {username: User}."""
    created: dict = {}
    for u in USERS_FIXED:
        existing = User.query.filter_by(username=u["username"]).first()
        if existing:
            created[u["username"]] = existing
            continue
        user = User(username=u["username"], email=u["email"], role=u["role"])
        user.set_password(u["password"])
        db.session.add(user)
        created[u["username"]] = user
    db.session.flush()
    return created


def seed_students(db, User, Student, users_map: dict) -> list:
    """Crea alumnos. Retorna lista de (Student, dict_data)."""
    result = []
    for sd in STUDENTS_DATA:
        existing_user = User.query.filter_by(username=sd["username"]).first()
        if existing_user:
            student = Student.query.filter_by(user_id=existing_user.id).first()
            if student:
                result.append((student, sd))
                continue

        user = User(username=sd["username"], email=sd["email"], role="student")
        user.set_password(sd["password"])
        db.session.add(user)
        db.session.flush()

        teacher = users_map.get(sd["teacher_username"])
        student = Student(
            user_id=user.id,
            teacher_id=teacher.id if teacher else None,
            full_name=sd["full_name"],
            national_id=sd["national_id"],
            grade=sd["grade"],
            section=sd["section"],
            age=sd["age"],
            tdah_type=sd["tdah_type"],
            tdah_confidence=0.0,
            address=sd["address"],
            emergency_contact_name=sd["emergency_contact_name"],
            emergency_contact_phone=sd["emergency_contact_phone"],
            tutor_full_name=sd["tutor_full_name"],
            tutor_relationship=sd["tutor_relationship"],
            tutor_phone=sd["tutor_phone"],
            tutor_email=sd["tutor_email"],
            tutor_national_id=sd["tutor_national_id"],
            tutor_whatsapp_enabled=True,
            allergies=sd.get("allergies"),
            medical_conditions=sd.get("medical_conditions"),
            medications=sd.get("medications"),
            notes=sd.get("notes"),
            created_at=rand_date(60, 90),
        )
        db.session.add(student)
        result.append((student, sd))

    db.session.flush()
    return result


def seed_reports(db, Report, students_list: list, users_map: dict) -> int:
    """Crea tests cognitivos y reportes del profesor."""
    total = 0
    test_types = ["vision_test", "audio_test", "stroop_test", "gonogo_test"]

    for student, sd in students_list:
        if Report.query.filter_by(student_id=student.id).count() > 0:
            continue

        tdah_type = sd["tdah_type"]
        teacher = users_map.get(sd["teacher_username"])

        # ── Tests cognitivos (3-5 por alumno) ────────────────────────────────
        # Garantizar al menos 1 de vision, stroop, gonogo; audio es opcional
        mandatory = ["vision_test", "stroop_test", "gonogo_test"]
        optional = ["audio_test"] if random.random() > 0.3 else []
        extra = random.choices(["vision_test", "stroop_test", "gonogo_test"], k=random.randint(0, 2))
        all_tests = mandatory + optional + extra

        base_date_offset = 58  # días atrás para el más antiguo
        for i, rtype in enumerate(all_tests):
            days_ago = base_date_offset - (i * random.randint(7, 12))
            days_ago = max(3, days_ago)
            content = make_test_content(tdah_type, rtype)
            content_json = json.dumps(content, ensure_ascii=False)
            report = Report(
                student_id=student.id,
                teacher_id=teacher.id if teacher else None,
                report_type=rtype,
                content=content_json,
                result_data=content_json,
                tipo_tdah=content["tipo_tdah"],
                confianza=content["confianza"],
                sent_to_parents=True,
                parent_email=sd["tutor_email"],
                created_at=rand_date(days_ago, days_ago + 5),
            )
            db.session.add(report)
            total += 1

        # ── Reportes narrativos del profesor (2 por alumno) ───────────────────
        templates = _TEACHER_REPORTS.get(tdah_type, _TEACHER_REPORTS["typical"])
        for idx, (content_text, recommendations) in enumerate(templates):
            days_ago = 40 - (idx * 18)
            add_comments = random.random() > 0.5
            report = Report(
                student_id=student.id,
                teacher_id=teacher.id if teacher else None,
                report_type="manual_teacher",
                content=content_text.format(name=sd["full_name"].split()[0]),
                recommendations=recommendations,
                parent_comments=_PARENT_COMMENTS[tdah_type] if add_comments else None,
                sent_to_parents=True,
                parent_email=sd["tutor_email"],
                tipo_tdah=tdah_type,
                confianza=0.0,
                created_at=rand_date(days_ago, days_ago + 6),
            )
            db.session.add(report)
            total += 1

    db.session.flush()
    return total


def seed_activities_and_sessions(db, Activity, Session, students_list: list, users_map: dict) -> tuple:
    """Crea actividades AR y sesiones por alumno."""
    act_count = 0
    ses_count = 0

    for student, sd in students_list:
        if Activity.query.filter_by(student_id=student.id).count() > 0:
            continue

        teacher = users_map.get(sd["teacher_username"])
        tdah_type = sd["tdah_type"]
        attn_min, attn_max = _ATTENTION_SCORES[tdah_type]
        time_min, time_max = _COMPLETION_TIMES[tdah_type]

        # Crear 2 actividades para el alumno
        chosen = random.sample(_AR_ACTIVITIES, 2)
        for act_data in chosen:
            activity = Activity(
                student_id=student.id,
                teacher_id=teacher.id if teacher else None,
                title=act_data["title"],
                description=act_data["description"],
                activity_type=act_data["activity_type"],
                difficulty_level=act_data["difficulty_level"],
                instructions=act_data["instructions"],
                ar_content=act_data["ar_content"],
                created_at=rand_date(45, 60),
            )
            db.session.add(activity)
            db.session.flush()
            act_count += 1

            # 2-3 sesiones por actividad
            num_sessions = random.randint(2, 3)
            for j in range(num_sessions):
                days_ago = 28 - (j * random.randint(6, 10))
                days_ago = max(1, days_ago)
                session = Session(
                    student_id=student.id,
                    activity_id=activity.id,
                    attention_score=round(random.uniform(attn_min, attn_max), 1),
                    completion_time=random.randint(time_min, time_max),
                    analysis_result={
                        "tipo_tdah": tdah_type,
                        "engagement": round(random.uniform(0.55, 0.95), 2),
                        "errores": random.randint(0, 5),
                    },
                    created_at=rand_date(days_ago, days_ago + 3),
                )
                db.session.add(session)
                ses_count += 1

    db.session.flush()
    return act_count, ses_count


def seed_notifications(db, Notification, students_list: list) -> int:
    """Crea 2-3 notificaciones por alumno."""
    total = 0
    for student, sd in students_list:
        if Notification.query.filter_by(user_id=student.user_id).count() > 0:
            continue

        first_name = sd["full_name"].split()[0]
        n_notifs = random.randint(2, 3)
        templates = random.sample(_NOTIF_TEMPLATES, n_notifs)

        for i, (ntype, title, message) in enumerate(templates):
            notif = Notification(
                user_id=student.user_id,
                title=title,
                message=message.format(name=first_name),
                type=ntype,
                is_read=(i > 0),  # la primera sin leer, el resto leídas
                related_student_id=student.id,
                created_at=rand_date(1, 14),
            )
            db.session.add(notif)
            total += 1

    db.session.flush()
    return total


def run_tdah_classification(students_list: list, db) -> int:
    """Ejecuta calcular_tipo_tdah() y persiste la clasificación."""
    classified = 0
    for student, sd in students_list:
        result = student.calcular_tipo_tdah()
        if result and result.get("tipo"):
            classified += 1
        else:
            # Fallback: asignar el tipo esperado directamente
            student.tdah_type = sd["tdah_type"]
            student.tdah_confidence = round(random.uniform(65, 85), 1)
            student.last_evaluation_date = rand_date(5, 20)
    db.session.flush()
    return classified


# ─────────────────────────────────────────────────────────────────────────────
# VERIFICACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def verify_data(db, models: dict, students_list: list, counters: dict) -> bool:
    Student = models["Student"]
    Report = models["Report"]
    Session = models["Session"]
    Notification = models["Notification"]
    User = models["User"]

    errors = []

    # Cada alumno tiene tdah_type
    for student, sd in students_list:
        db.session.refresh(student)
        if not student.tdah_type:
            errors.append(f"  ERROR: {sd['full_name']} no tiene tdah_type asignado")

    # Cada profesor tiene al menos 3 alumnos
    for username in ["prof_maria", "prof_carlos"]:
        teacher = User.query.filter_by(username=username).first()
        if teacher:
            count = Student.query.filter_by(teacher_id=teacher.id).count()
            if count < 3:
                errors.append(f"  ERROR: {username} tiene solo {count} alumnos (mínimo 3)")

    # Totales de filas
    total_reports = Report.query.count()
    total_sessions = Session.query.count()
    total_notifs = Notification.query.count()

    if total_reports < counters.get("reports", 0):
        errors.append(f"  ERROR: Se esperaban {counters['reports']} reports, hay {total_reports}")
    if total_sessions < counters.get("sessions", 0):
        errors.append(f"  ERROR: Se esperaban {counters['sessions']} sessions, hay {total_sessions}")
    if total_notifs < counters.get("notifications", 0):
        errors.append(f"  ERROR: Se esperaban {counters['notifications']} notificaciones, hay {total_notifs}")

    if errors:
        print("\n⚠️  VERIFICACIÓN FALLÓ:")
        for e in errors:
            print(e)
        return False

    print(f"\n✅ Verificación OK — {total_reports} reportes, {total_sessions} sesiones, {total_notifs} notifs")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENTO DE CREDENCIALES
# ─────────────────────────────────────────────────────────────────────────────

def generate_credentials_doc(models: dict, db) -> None:
    Report = models["Report"]
    Session = models["Session"]
    Notification = models["Notification"]
    Student = models["Student"]
    User = models["User"]

    docs_dir = os.path.join(PROJECT_ROOT, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    filepath = os.path.join(docs_dir, "demo_credentials.md")

    lines = [
        "# Credenciales Demo — Defensa de Tesis",
        "",
        "> Generado automáticamente por `scripts/seed_demo.py`",
        f"> Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Colegio",
        "**Unidad Educativa San Martín de Porres** — Cochabamba, Bolivia",
        "",
        "---",
        "",
        "## Usuarios del sistema",
        "",
        "| Rol | Usuario | Contraseña | Email |",
        "|-----|---------|-----------|-------|",
        "| Admin | `admin` | `admin123` | admin@sanmartin.edu.bo |",
        "| Docente | `prof_maria` | `prof123` | m.quispe@sanmartin.edu.bo |",
        "| Docente | `prof_carlos` | `prof123` | c.mamani@sanmartin.edu.bo |",
        "",
        "---",
        "",
        "## Alumnos",
        "",
        "| Alumno | Usuario | Contraseña | Tipo TDAH | Grado | Docente |",
        "|--------|---------|-----------|-----------|-------|---------|",
    ]

    for sd in STUDENTS_DATA:
        user = User.query.filter_by(username=sd["username"]).first()
        if not user:
            continue
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            continue
        teacher_user = User.query.get(student.teacher_id) if student.teacher_id else None
        teacher_name = teacher_user.username if teacher_user else "-"
        tdah_display = {
            "typical": "Típico (sin TDAH)",
            "inatento": "Inatento",
            "hiperactivo": "Hiperactivo",
            "combinado": "Combinado",
        }.get(sd["tdah_type"], sd["tdah_type"])
        lines.append(
            f"| {sd['full_name']} | `{sd['username']}` | `estudiante123` | {tdah_display} | {sd['grade']} {sd['section']} | {teacher_name} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Estadísticas de datos generados",
        "",
    ]

    for sd in STUDENTS_DATA:
        user = User.query.filter_by(username=sd["username"]).first()
        if not user:
            continue
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            continue
        n_tests = Report.query.filter(
            Report.student_id == student.id,
            Report.report_type != "manual_teacher",
        ).count()
        n_teacher_reports = Report.query.filter_by(
            student_id=student.id, report_type="manual_teacher"
        ).count()
        n_sessions = Session.query.filter_by(student_id=student.id).count()
        n_notifs = Notification.query.filter_by(user_id=user.id).count()
        confidence = f"{student.tdah_confidence:.0f}%" if student.tdah_confidence else "—"
        lines.append(
            f"- **{sd['full_name']}** ({sd['tdah_type']}, confianza {confidence}): "
            f"{n_tests} tests, {n_teacher_reports} reportes docente, {n_sessions} sesiones AR, {n_notifs} notifs"
        )

    lines += [
        "",
        "---",
        "",
        "## Guía rápida para la defensa",
        "",
        "### Demostrar cada tipo de TDAH",
        "- **Sin TDAH (típico):** login con `sofia.quispe` o `mateo.mamani`",
        "- **TDAH Inatento:** login con `valeria.choque` o `diego.condori`",
        "- **TDAH Hiperactivo:** login con `camila.ticona` o `sebastian.apaza`",
        "- **TDAH Combinado:** login con `isabella.villca` o `joaquin.calle`",
        "",
        "### Flujo recomendado para demo",
        "1. Login como `admin/admin123` → ver dashboard con métricas globales",
        "2. Inscribir alumno nuevo (wizard 3 pasos)",
        "3. Login como `prof_maria/prof123` → ver grid de alumnos",
        "4. Click en Valeria Choque → ver tabs de progreso, tests, actividades AR",
        "5. Crear reporte con asistencia IA",
        "6. Login como `valeria.choque/estudiante123` → ver dashboard personal",
        "",
        "---",
        "*Generado por `scripts/seed_demo.py` — no editar manualmente*",
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  📄 Credenciales guardadas en: docs/demo_credentials.md")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed de datos demo para TDAH Platform")
    parser.add_argument("--reset", action="store_true", help="Borra todos los datos y los recrea")
    parser.add_argument("--yes", action="store_true", help="Salta la confirmación interactiva (usar solo en scripts)")
    args = parser.parse_args()

    start = time.time()

    from app import create_app
    from app.extensions import db
    from app.core.models.user import User
    from app.core.models.student import Student
    from app.core.models.activity import Activity, Session
    from app.core.models.report import Report
    from app.core.models.notification import Notification

    models = {
        "User": User,
        "Student": Student,
        "Activity": Activity,
        "Session": Session,
        "Report": Report,
        "Notification": Notification,
    }

    app = create_app("development")

    with app.app_context():
        print("\n" + "=" * 60)
        print("  SEED DE DATOS DEMO — TDAH Platform")
        print("=" * 60)

        if args.reset:
            if not args.yes:
                confirm = input("\n  ⚠️  Esto borrará TODOS los datos del sistema.\n  Escribe BORRAR para continuar: ")
                if confirm.strip() != "BORRAR":
                    print("  Operación cancelada.")
                    sys.exit(0)
            reset_database(db, models)

        # Verificar idempotencia
        existing_admin = User.query.filter_by(username="admin").first()
        if existing_admin and not args.reset:
            print("\n  Los datos demo ya existen.")
            print("  Usa --reset para borrar y recrear desde cero.")
            print(f"\n  Admin:      admin / admin123")
            print(f"  Docentes:   prof_maria / prof123  |  prof_carlos / prof123")
            print(f"  Alumnos:    estudiante123")
            sys.exit(0)

        print("\n  [1/6] Creando usuarios fijos...")
        users_map = seed_users(db, User)
        print(f"        {len(users_map)} usuarios (admin + 2 docentes)")

        print("  [2/6] Creando alumnos...")
        students_list = seed_students(db, User, Student, users_map)
        db.session.commit()
        print(f"        {len(students_list)} alumnos creados")

        print("  [3/6] Generando tests cognitivos y reportes docente...")
        n_reports = seed_reports(db, Report, students_list, users_map)
        db.session.commit()
        print(f"        {n_reports} reportes generados")

        print("  [4/6] Generando actividades AR y sesiones...")
        n_acts, n_sessions = seed_activities_and_sessions(db, Activity, Session, students_list, users_map)
        db.session.commit()
        print(f"        {n_acts} actividades, {n_sessions} sesiones")

        print("  [5/6] Ejecutando algoritmo de clasificación TDAH...")
        classified = run_tdah_classification(students_list, db)
        db.session.commit()
        print(f"        {classified}/{len(students_list)} alumnos clasificados por el algoritmo")

        print("  [6/7] Generando notificaciones...")
        n_notifs = seed_notifications(db, Notification, students_list)
        db.session.commit()
        print(f"        {n_notifs} notificaciones creadas")

        print("  [7/7] Otorgando insignias...")
        try:
            from app.services.badge_service import ensure_badges_exist, check_and_award_badges
            ensure_badges_exist()
            total_badges = 0
            for student, _ in students_list:
                awarded = check_and_award_badges(student)
                total_badges += len(awarded)
            print(f"        {total_badges} insignias otorgadas")
        except Exception as e:
            print(f"        Badges omitidos: {e}")

        counters = {
            "reports": n_reports,
            "sessions": n_sessions,
            "notifications": n_notifs,
        }

        # ── Verificación ──────────────────────────────────────────────────────
        ok = verify_data(db, models, students_list, counters)
        if not ok:
            sys.exit(1)

        # ── Generar doc de credenciales ───────────────────────────────────────
        generate_credentials_doc(models, db)

        # ── Resumen final ─────────────────────────────────────────────────────
        elapsed = time.time() - start
        print("\n" + "=" * 60)
        print("  RESUMEN")
        print("=" * 60)
        print(f"  Usuarios creados:    {len(users_map)} (1 admin + 2 docentes)")
        print(f"  Alumnos creados:     {len(students_list)}")

        by_type: dict = {}
        for student, sd in students_list:
            by_type.setdefault(sd["tdah_type"], []).append(sd["full_name"].split()[0])
        for t, names in by_type.items():
            print(f"    {t:12} → {', '.join(names)}")

        print(f"  Tests generados:     {Report.query.filter(Report.report_type != 'manual_teacher').count()}")
        print(f"  Reportes docente:    {Report.query.filter_by(report_type='manual_teacher').count()}")
        print(f"  Sesiones AR:         {Session.query.count()}")
        print(f"  Notificaciones:      {Notification.query.count()}")
        print(f"\n  Tiempo total:        {elapsed:.1f}s")
        print("\n  Credenciales de acceso:")
        print("    admin         / admin123")
        print("    prof_maria    / prof123")
        print("    prof_carlos   / prof123")
        print("    (alumnos)     / estudiante123")
        print("\n  Ver docs/demo_credentials.md para guía completa de defensa.")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
