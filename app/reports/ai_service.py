"""
Servicio de IA — Anthropic Claude
Genera análisis estructurados para apoyo pedagógico.
"""
import json
from anthropic import Anthropic
from flask import current_app


class AIService:
    """Wrapper sobre Anthropic Claude para generación de análisis pedagógicos."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            api_key = current_app.config.get('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY no configurada. Agregala al .env "
                    "o a las variables de entorno de Railway."
                )
            self._client = Anthropic(api_key=api_key)
        return self._client

    def chat(self, system_prompt, user_prompt, temperature=None, max_tokens=None):
        """
        Envía un mensaje a Claude y retorna el texto de la respuesta.

        Args:
            system_prompt: instrucciones de rol/contexto
            user_prompt: pregunta o tarea específica
            temperature: creatividad (default: config AI_TEMPERATURE)
            max_tokens: tokens máximos (default: config AI_MAX_TOKENS)

        Returns:
            str: respuesta del modelo
        """
        client = self._get_client()
        temp = temperature if temperature is not None else current_app.config.get('AI_TEMPERATURE', 0.3)
        tokens = max_tokens or current_app.config.get('AI_MAX_TOKENS', 1500)
        model = current_app.config.get('AI_MODEL', 'claude-haiku-4-5')

        try:
            response = client.messages.create(
                model=model,
                max_tokens=tokens,
                temperature=temp,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            current_app.logger.error(f"Error llamando a Claude: {e}")
            raise

    def chat_json(self, system_prompt, user_prompt, temperature=None, max_tokens=None):
        """
        Igual que chat() pero garantiza que la respuesta sea JSON válido.

        Returns:
            dict: respuesta parseada
        """
        json_instruction = (
            "\n\nIMPORTANTE: Responde ÚNICAMENTE con un objeto JSON válido. "
            "Sin texto antes ni después del JSON. Sin bloques de código markdown. "
            "Solo el JSON crudo."
        )
        raw = self.chat(system_prompt + json_instruction, user_prompt, temperature, max_tokens)

        cleaned = raw.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            current_app.logger.error(
                f"JSON inválido de Claude: {e}\nRespuesta cruda: {raw}"
            )
            raise ValueError(f"Claude devolvió JSON inválido: {e}")

    # ── Métodos de dominio ────────────────────────────────────────────────────

    def generate_teacher_report(self, student_data, period="mensual"):
        """
        Genera reporte pedagógico completo para profesor.

        Args:
            student_data: dict con datos del estudiante
            period: periodo del reporte

        Returns:
            dict con claves: resumen_ejecutivo, fortalezas, areas_mejora,
                             recomendaciones, prediccion_progreso, alertas
        """
        system_prompt = (
            "Eres un asistente pedagógico especializado en TDAH infantil que trabaja "
            "con docentes en Bolivia. Analizas datos de estudiantes de 9 a 12 años y "
            "generas reportes profesionales con recomendaciones basadas en evidencia. "
            "NO emitas diagnósticos clínicos. Usa lenguaje claro y empático. "
            "NUNCA sugieras medicación. Siempre respondes en español latinoamericano."
        )

        user_prompt = f"""Genera un reporte {period} para:

Estudiante: {student_data.get('username')}
Tipo TDAH: {student_data.get('tdah_type', 'En evaluación')}
Confianza diagnóstico: {student_data.get('tdah_confidence', 0)}%

Tests completados: {student_data.get('total_tests', 0)}
Promedio atención: {student_data.get('avg_attention', 0)}%

Historial reciente:
{json.dumps(student_data.get('recent_history', []), indent=2, ensure_ascii=False)}

Genera un JSON con:
{{
    "resumen_ejecutivo": "Resumen de 2-3 líneas",
    "fortalezas": ["fortaleza 1", "fortaleza 2"],
    "areas_mejora": ["área 1", "área 2"],
    "recomendaciones": [
        {{
            "titulo": "Recomendación específica y aplicable en aula boliviana",
            "descripcion": "Cómo implementarla",
            "prioridad": "alta/media/baja",
            "evidencia": "Qué dato del análisis la justifica"
        }}
    ],
    "prediccion_progreso": "Predicción basada en datos",
    "alertas": ["alerta si existe"]
}}"""

        try:
            return self.chat_json(system_prompt, user_prompt, temperature=0.3)
        except Exception as e:
            current_app.logger.error(f"Error generando reporte docente: {e}")
            return {
                "resumen_ejecutivo": "El servicio de análisis IA no está disponible en este momento. Podés redactar el reporte manualmente o contactar al administrador.",
                "fortalezas": [],
                "areas_mejora": [],
                "recomendaciones": [],
                "prediccion_progreso": "",
                "alertas": []
            }

    def generate_student_recommendation(self, student_data):
        """
        Genera recomendación de actividad para estudiante.

        Args:
            student_data: {username, tdah_type, recent_scores, last_activity}

        Returns:
            dict: {activity, reason, difficulty}
        """
        system_prompt = (
            "Eres ARty, un asistente virtual amigable para niños con TDAH. "
            "Tu trabajo es recomendar actividades educativas de manera motivadora y clara."
        )

        user_prompt = f"""Estudiante: {student_data['username']}
Tipo TDAH: {student_data.get('tdah_type', 'No determinado')}
Actividad anterior: {student_data.get('last_activity', 'Ninguna')}
Puntajes recientes: {student_data.get('recent_scores', [])}

Recomienda la mejor actividad para este estudiante.

Responde en JSON:
{{
    "activity": "nombre de la actividad",
    "reason": "explicación motivadora",
    "difficulty": "fácil/medio/difícil"
}}"""

        try:
            return self.chat_json(system_prompt, user_prompt, temperature=0.5)
        except Exception:
            return {
                "activity": "Test de Atención Visual",
                "reason": "Es un buen punto de partida para medir tu atención.",
                "difficulty": "medio"
            }

    # Vocabulario cerrado de áreas. La IA debe elegir de acá y no inventar,
    # para que el histórico de sesiones sea comparable entre sí.
    AREAS_PEDAGOGICAS = {
        'atencion_sostenida': 'Atención sostenida',
        'atencion_selectiva': 'Atención selectiva',
        'control_inhibitorio': 'Control inhibitorio',
        'memoria_trabajo': 'Memoria de trabajo',
        'flexibilidad_cognitiva': 'Flexibilidad cognitiva',
        'planificacion': 'Planificación y organización',
        'autorregulacion': 'Autorregulación emocional',
    }

    def generate_pedagogical_recommendation(self, context):
        """Recomienda la próxima sesión pedagógica presencial para un alumno.

        Args:
            context: dict con perfil del alumno, tests recientes, actividades
                     AR e historial de sesiones pedagógicas.

        Returns:
            dict con: area, area_label, level, session_title, activity_type,
                      rationale, evidence, objectives, duration_min, materials
        """
        areas = '\n'.join(
            f'- {slug}: {label}' for slug, label in self.AREAS_PEDAGOGICAS.items()
        )

        system_prompt = (
            "Eres un asistente pedagógico especializado en TDAH infantil que trabaja "
            "con docentes de primaria en Bolivia. Diseñás sesiones de trabajo "
            "PRESENCIALES y de bajo costo: papel, lápiz, objetos del aula. NO propongas "
            "apps, pantallas ni material que haya que comprar. "
            "NO emitas diagnósticos clínicos y NUNCA sugieras medicación. "
            "Trabajás con niños de 8 a 12 años. Respondés en español latinoamericano, "
            "con lenguaje concreto y accionable para el docente."
        )

        user_prompt = f"""Recomendá la PRÓXIMA sesión pedagógica presencial para este alumno.

## Perfil
Nombre: {context.get('nombre')}
Edad: {context.get('edad') or 'no registrada'}
Curso: {context.get('curso') or 'no registrado'}
Perfil TDAH detectado: {context.get('perfil_tdah')}
Confianza del análisis: {context.get('confianza', 0)}%

## Tests cognitivos recientes
{json.dumps(context.get('tests', []), indent=2, ensure_ascii=False) or 'Sin tests registrados'}

## Actividades AR recientes
{json.dumps(context.get('ar', []), indent=2, ensure_ascii=False) or 'Sin actividades AR'}

## Sesiones pedagógicas previas
{json.dumps(context.get('sesiones_previas', []), indent=2, ensure_ascii=False) or 'Ninguna: es la primera sesión'}

## Áreas disponibles (elegí UNA, usá el slug exacto)
{areas}

## Criterios
- Si no hay sesiones previas, empezá por el área más débil según los tests, nivel 1 o 2.
- Si hay sesiones previas evaluadas con buen puntaje (>= 70), subí un nivel o cambiá de área.
- Si el último puntaje fue bajo (< 50), repetí el área bajando un nivel.
- El nivel va de 1 (muy guiado) a 5 (autónomo).
- Justificá con datos concretos del historial, no con generalidades.

Devolvé un JSON con exactamente esta forma:
{{
    "area": "slug exacto de la lista",
    "level": 3,
    "session_title": "Título corto y concreto de la sesión",
    "activity_type": "Tipo de actividad en 2-4 palabras",
    "duration_min": 20,
    "rationale": "2-3 líneas explicando por qué esta área y este nivel",
    "evidence": ["dato concreto del historial que justifica la elección"],
    "objectives": ["objetivo observable de la sesión"],
    "materials": ["material de aula, barato o reciclable"]
}}"""

        data = self.chat_json(system_prompt, user_prompt, temperature=0.4, max_tokens=1200)

        # La IA puede devolver un área fuera del vocabulario: la normalizamos
        # antes de persistirla para no ensuciar el histórico.
        area = (data.get('area') or '').strip().lower()
        if area not in self.AREAS_PEDAGOGICAS:
            area = 'atencion_sostenida'
        data['area'] = area
        data['area_label'] = self.AREAS_PEDAGOGICAS[area]

        try:
            level = int(data.get('level') or 1)
        except (TypeError, ValueError):
            level = 1
        data['level'] = min(5, max(1, level))

        for campo in ('evidence', 'objectives', 'materials'):
            valor = data.get(campo)
            if isinstance(valor, str):
                data[campo] = [valor]
            elif not isinstance(valor, list):
                data[campo] = []

        return data

    def generate_session_plan(self, context, recommendation):
        """Convierte una recomendación en el material concreto de la sesión.

        Returns:
            dict con: teacher_guide (markdown-ish en texto plano),
                      student_worksheet (texto de la hoja del niño),
                      rubric {criterios: [{nombre, descripcion, niveles}]}
        """
        system_prompt = (
            "Eres un asistente pedagógico especializado en TDAH infantil que prepara "
            "material PRESENCIAL para docentes de primaria en Bolivia. Escribís guías "
            "que un docente puede seguir sin formación clínica previa, y hojas de "
            "trabajo que se imprimen en blanco y negro en una fotocopiadora común. "
            "Solo papel, lápiz y objetos del aula: nada de pantallas ni material que "
            "haya que comprar. NO emitas diagnósticos clínicos ni menciones medicación. "
            "Respondés en español latinoamericano."
        )

        user_prompt = f"""Preparás el material para esta sesión con {context.get('nombre')}
(edad {context.get('edad') or 'primaria'}, perfil {context.get('perfil_tdah')}).

## Sesión a preparar
Título: {recommendation.get('session_title')}
Área: {recommendation.get('area_label')}
Nivel: {recommendation.get('level')} de 5
Duración: {recommendation.get('duration_min')} minutos
Tipo: {recommendation.get('activity_type')}
Objetivos: {json.dumps(recommendation.get('objectives', []), ensure_ascii=False)}
Materiales: {json.dumps(recommendation.get('materials', []), ensure_ascii=False)}

Devolvé un JSON con esta forma exacta:
{{
    "teacher_guide": "Guía paso a paso para el docente. Usá pasos numerados '1. ' '2. '. Incluí: preparación previa, consigna textual para decirle al niño, desarrollo por etapas con tiempos, qué observar, y qué hacer si el niño se frustra o se desregula.",
    "student_worksheet": "Contenido EXACTO de la hoja del niño, lista para imprimir. Consignas cortas y en segunda persona. Si la actividad necesita casilleros, tablas o espacios para marcar, dibujalos con caracteres de texto.",
    "rubric": {{
        "criterios": [
            {{
                "nombre": "Nombre corto del criterio",
                "descripcion": "Qué observa el docente",
                "niveles": {{
                    "logrado": "Qué se ve cuando está logrado",
                    "en_proceso": "Qué se ve cuando está en proceso",
                    "inicial": "Qué se ve cuando recién empieza"
                }}
            }}
        ],
        "metricas_a_registrar": ["nombre de un dato numérico que el docente debe contar durante la sesión"]
    }}
}}"""

        # 16k: la guía + la hoja del alumno + la rúbrica en un solo JSON se pasan
        # largo. Con 3000 la respuesta se cortaba a la mitad y el JSON no parseaba.
        data = self.chat_json(system_prompt, user_prompt, temperature=0.4, max_tokens=16000)

        rubric = data.get('rubric')
        if not isinstance(rubric, dict):
            rubric = {}
        if not isinstance(rubric.get('criterios'), list):
            rubric['criterios'] = []
        if not isinstance(rubric.get('metricas_a_registrar'), list):
            rubric['metricas_a_registrar'] = []
        data['rubric'] = rubric

        for campo in ('teacher_guide', 'student_worksheet'):
            if not isinstance(data.get(campo), str):
                data[campo] = ''

        return data

    GRADES = ['Necesita apoyo', 'Regular', 'Bueno', 'Excelente']

    def analyze_session_result(self, context, session, teacher_notes, objective_metrics):
        """Analiza lo que el docente reportó después de la sesión presencial.

        Returns:
            dict con: analysis, score (0-100), grade, next_recommendation
        """
        system_prompt = (
            "Eres un asistente pedagógico especializado en TDAH infantil. Analizás el "
            "reporte que un docente escribió después de una sesión presencial y devolvés "
            "una lectura útil y honesta: qué funcionó, qué no, y qué conviene hacer la "
            "próxima vez. Sos concreto y no adulás: si el resultado fue pobre, decilo con "
            "respeto y proponé un ajuste. NO emitas diagnósticos clínicos ni menciones "
            "medicación. Respondés en español latinoamericano."
        )

        user_prompt = f"""Analizá el resultado de esta sesión.

## Alumno
{context.get('nombre')} · {context.get('perfil_tdah')} · confianza {context.get('confianza', 0)}%

## Sesión realizada
Título: {session.session_title}
Área: {session.session_area}
Nivel: {session.session_level} de 5
Objetivos que se buscaban: {json.dumps((session.ai_recommendation or {}).get('objectives', []), ensure_ascii=False)}
Rúbrica: {json.dumps((session.rubric or {}).get('criterios', []), indent=2, ensure_ascii=False)}

## Lo que reportó el docente
{teacher_notes}

## Métricas objetivas registradas
{json.dumps(objective_metrics or {}, indent=2, ensure_ascii=False) or 'No se registraron métricas numéricas'}

## Criterios de puntaje
- 85-100 Excelente: cumplió los objetivos con autonomía.
- 70-84 Bueno: los cumplió con apoyo puntual.
- 50-69 Regular: los cumplió parcialmente, necesitó apoyo sostenido.
- 0-49 Necesita apoyo: no llegó a los objetivos; hay que bajar el nivel o cambiar el abordaje.

Devolvé un JSON con esta forma exacta:
{{
    "analysis": "3-5 líneas leyendo el desempeño contra los objetivos y la rúbrica. Citá los datos que reportó el docente.",
    "score": 72,
    "grade": "uno de: Excelente / Bueno / Regular / Necesita apoyo",
    "next_recommendation": "2-3 líneas: qué hacer en la próxima sesión y por qué (subir nivel, repetir area, cambiar de area)."
}}"""

        data = self.chat_json(system_prompt, user_prompt, temperature=0.3, max_tokens=1500)

        try:
            score = float(data.get('score'))
        except (TypeError, ValueError):
            score = 0.0
        data['score'] = min(100.0, max(0.0, score))

        grade = (data.get('grade') or '').strip()
        if grade not in self.GRADES:
            # Derivamos la calificación del puntaje si el modelo devolvió otra cosa
            if score >= 85:
                grade = 'Excelente'
            elif score >= 70:
                grade = 'Bueno'
            elif score >= 50:
                grade = 'Regular'
            else:
                grade = 'Necesita apoyo'
        data['grade'] = grade

        for campo in ('analysis', 'next_recommendation'):
            if not isinstance(data.get(campo), str):
                data[campo] = ''

        return data

    def answer_parent_question(self, question, student_context):
        """
        Responde preguntas de padres sobre TDAH y progreso del hijo.

        Returns:
            str: respuesta en lenguaje simple
        """
        system_prompt = (
            "Eres FamilyGuide, un asistente amable y profesional que ayuda a padres "
            "de niños con TDAH en Bolivia. Explicas conceptos en lenguaje simple y "
            "comprensible. Eres empático, positivo y ofreces consejos prácticos. "
            "NUNCA sugieras medicación. Respondes en español de manera conversacional."
        )

        user_prompt = f"""Pregunta del padre/madre: {question}

Contexto del hijo/a:
Nombre: {student_context.get('username')}
Tipo TDAH: {student_context.get('tdah_type', 'En evaluación')}
Progreso reciente: {student_context.get('progress_summary', 'Información no disponible')}

Responde de manera clara, empática y práctica."""

        try:
            return self.chat(system_prompt, user_prompt, temperature=0.6)
        except Exception:
            return "El servicio de IA no está disponible en este momento. Por favor consultá con el docente directamente."

    def generate_simple_explanation(self, metric_name, value, context):
        """
        Genera explicación simple de una métrica para padres.

        Returns:
            str: explicación en 2-3 oraciones
        """
        system_prompt = (
            "Eres un asistente que explica métricas educativas a padres. "
            "Usa analogías simples y evita tecnicismos. Sé breve (2-3 oraciones máximo)."
        )

        user_prompt = f"""Explica de forma simple qué significa:

Métrica: {metric_name}
Valor: {value}
Contexto: {context}

Responde en lenguaje simple que cualquier padre pueda entender."""

        try:
            return self.chat(system_prompt, user_prompt, temperature=0.5, max_tokens=200)
        except Exception:
            return f"El valor de {metric_name} es {value}."


# Instancia global del servicio
ai_service = AIService()
