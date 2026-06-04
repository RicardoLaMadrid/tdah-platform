"""
Servicio de Inteligencia Artificial usando OpenAI GPT
"""
from openai import OpenAI
from flask import current_app
import json

class AIService:
    """Servicio centralizado para interacciones con OpenAI GPT"""
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Inicializa el cliente de OpenAI"""
        if not self.client:
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY no configurada")
            self.client = OpenAI(api_key=api_key)
        return self.client
    
    def chat(self, messages, system_prompt=None, temperature=None, max_tokens=None, json_mode=False):
        """
        Envía mensajes a GPT y obtiene respuesta
        
        Args:
            messages: Lista de mensajes [{"role": "user", "content": "..."}]
            system_prompt: Prompt del sistema (opcional)
            temperature: Creatividad (0-1, default: 0.7)
            max_tokens: Tokens máximos (default: 2000)
            json_mode: Forzar respuesta en JSON
        
        Returns:
            str: Respuesta de GPT
        """
        try:
            client = self._get_client()
            
            # Configuración
            temp = temperature or current_app.config.get('AI_TEMPERATURE', 0.7)
            tokens = max_tokens or current_app.config.get('AI_MAX_TOKENS', 2000)
            model = current_app.config.get('AI_MODEL', 'gpt-4o-mini')
            
            # Construir mensajes
            chat_messages = []
            
            if system_prompt:
                chat_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            chat_messages.extend(messages)
            
            # Configurar parámetros
            kwargs = {
                "model": model,
                "messages": chat_messages,
                "temperature": temp,
                "max_tokens": tokens
            }
            
            # Modo JSON si se requiere
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            # Llamada a la API
            response = client.chat.completions.create(**kwargs)
            
            # Extraer texto de la respuesta
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Error en AIService.chat: {e}")
            return f"Lo siento, hubo un error al procesar tu solicitud: {str(e)}"
    
    def generate_student_recommendation(self, student_data):
        """
        Genera recomendación de actividad para estudiante
        
        Args:
            student_data: {
                'username': str,
                'tdah_type': str,
                'recent_scores': list,
                'last_activity': str
            }
        
        Returns:
            dict: {'activity': str, 'reason': str, 'difficulty': str}
        """
        system_prompt = """Eres ARty, un asistente virtual amigable para niños con TDAH. 
Tu trabajo es recomendar actividades educativas de manera motivadora y clara.
Responde SIEMPRE en formato JSON válido."""
        
        user_prompt = f"""Estudiante: {student_data['username']}
Tipo TDAH: {student_data.get('tdah_type', 'No determinado')}
Actividad anterior: {student_data.get('last_activity', 'Ninguna')}
Puntajes recientes: {student_data.get('recent_scores', [])}

Recomienda la mejor actividad para este estudiante.

Responde en JSON con esta estructura:
{{
    "activity": "nombre de la actividad",
    "reason": "explicación motivadora",
    "difficulty": "fácil/medio/difícil"
}}"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.chat(
            messages, 
            system_prompt=system_prompt, 
            temperature=0.5,
            json_mode=True
        )
        
        try:
            result = json.loads(response)
            return result
        except:
            return {
                "activity": "Test de Atención Visual",
                "reason": "Es un buen punto de partida para medir tu atención.",
                "difficulty": "medio"
            }
    
    def generate_teacher_report(self, student_data, period="mensual"):
        """
        Genera reporte pedagógico completo para profesor
        
        Args:
            student_data: Datos completos del estudiante
            period: Periodo del reporte
        
        Returns:
            dict: Reporte estructurado
        """
        system_prompt = """Eres TeacherGPT, un asistente pedagógico experto en TDAH.
Analizas datos de estudiantes y generas reportes profesionales con recomendaciones basadas en evidencia científica.
Siempre respondes en español y en formato JSON válido."""
        
        user_prompt = f"""Genera un reporte {period} para:

Estudiante: {student_data.get('username')}
Tipo TDAH: {student_data.get('tdah_type', 'En evaluación')}
Confianza diagnóstico: {student_data.get('tdah_confidence', 0)}%

Tests completados: {student_data.get('total_tests', 0)}
Promedio atención: {student_data.get('avg_attention', 0)}%

Historial reciente:
{json.dumps(student_data.get('recent_history', []), indent=2)}

Genera un JSON con:
{{
    "resumen_ejecutivo": "Resumen de 2-3 líneas",
    "fortalezas": ["fortaleza 1", "fortaleza 2"],
    "areas_mejora": ["área 1", "área 2"],
    "recomendaciones": [
        {{
            "titulo": "Recomendación específica",
            "descripcion": "Cómo implementarla",
            "prioridad": "alta/media/baja",
            "evidencia": "Base científica"
        }}
    ],
    "prediccion_progreso": "Predicción basada en datos",
    "alertas": ["alerta 1 si existe", "alerta 2 si existe"]
}}"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.chat(
            messages, 
            system_prompt=system_prompt, 
            temperature=0.3,
            json_mode=True
        )
        
        try:
            return json.loads(response)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return {
                "resumen_ejecutivo": "Error al generar reporte",
                "recomendaciones": [],
                "alertas": []
            }
    
    def answer_parent_question(self, question, student_context):
        """
        Responde preguntas de padres sobre TDAH y progreso de hijo
        
        Args:
            question: Pregunta del padre
            student_context: Contexto del estudiante
        
        Returns:
            str: Respuesta en lenguaje simple
        """
        system_prompt = """Eres FamilyGuide, un asistente amable y profesional que ayuda a padres de niños con TDAH.
Explicas conceptos médicos y pedagógicos en lenguaje simple y comprensible.
Eres empático, positivo y siempre ofreces consejos prácticos basados en evidencia.
Respondes en español de manera natural y conversacional."""
        
        user_prompt = f"""Pregunta del padre/madre: {question}

Contexto del hijo/a:
Nombre: {student_context.get('username')}
Tipo TDAH: {student_context.get('tdah_type', 'En evaluación')}
Progreso reciente: {student_context.get('progress_summary', 'Información no disponible')}

Responde de manera clara, empática y práctica. No uses tecnicismos innecesarios."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        return self.chat(messages, system_prompt=system_prompt, temperature=0.6)
    
    def generate_simple_explanation(self, metric_name, value, context):
        """
        Genera explicación simple de una métrica para padres
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor de la métrica
            context: Contexto adicional
        
        Returns:
            str: Explicación simple
        """
        system_prompt = """Eres un asistente que explica métricas educativas a padres.
Usa analogías simples y evita tecnicismos.
Sé breve (2-3 oraciones máximo)."""
        
        user_prompt = f"""Explica de forma simple qué significa:

Métrica: {metric_name}
Valor: {value}
Contexto: {context}

Responde en lenguaje simple que cualquier padre pueda entender."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        return self.chat(messages, system_prompt=system_prompt, temperature=0.5, max_tokens=200)


# Instancia global del servicio
ai_service = AIService()