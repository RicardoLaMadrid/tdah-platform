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
