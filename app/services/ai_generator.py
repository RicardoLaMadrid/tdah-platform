"""
app/services/ai_generator.py

Generador de actividades personalizadas para estudiantes con TDAH.
Usa OpenAI GPT cuando hay API key disponible; usa fallback local si no.
"""
import json
import random
from typing import Dict, List, Optional


# ══════════════════════════════════════════════════════════════════
#  BANCO DE ACTIVIDADES POR SUBTIPO (fallback sin API key)
# ══════════════════════════════════════════════════════════════════

ACTIVITIES_BANK = {
    'inatento': [
        {
            'title': 'Encuentra las Diferencias',
            'description': 'Compara dos imágenes y encuentra los 5 elementos distintos.',
            'activity_type': 'atencion',
            'instructions': '1. Observa ambas imágenes durante 30 segundos\n2. Marca cada diferencia que encuentres\n3. Tómate tu tiempo, no hay prisa',
            'objectives': ['Mejorar atención sostenida', 'Desarrollar percepción visual detallada'],
            'difficulty_level': 1,
            'duration_minutes': 10,
            'tips_for_teacher': 'Si el estudiante se distrae, señala una zona específica para redirigir su atención.',
            'tips_for_parent': 'Realiza esta actividad en un ambiente sin distracciones.',
            'ar_content': {'enabled': True, 'type': 'markerless', 'description': 'Objetos 3D comparables'}
        },
        {
            'title': 'Clasificador de Objetos',
            'description': 'Agrupa objetos según su categoría antes de que el tiempo se acabe.',
            'activity_type': 'organizacion',
            'instructions': '1. Observa todos los objetos en pantalla\n2. Arrastra cada uno a su categoría correcta\n3. Completa antes del tiempo límite',
            'objectives': ['Mejorar organización', 'Entrenar atención selectiva'],
            'difficulty_level': 2,
            'duration_minutes': 8,
            'tips_for_teacher': 'Empieza con pocas categorías y aumenta gradualmente.',
            'tips_for_parent': 'Celebra cada logro, aunque sea pequeño.',
            'ar_content': {'enabled': False}
        },
        {
            'title': 'Secuencia de Pasos',
            'description': 'Sigue una secuencia de instrucciones paso a paso sin saltarte ninguno.',
            'activity_type': 'atencion',
            'instructions': '1. Lee cada paso antes de ejecutarlo\n2. Completa los pasos en orden\n3. Si te pierdes, vuelve al inicio',
            'objectives': ['Mejorar seguimiento de instrucciones', 'Reducir errores de omisión'],
            'difficulty_level': 2,
            'duration_minutes': 12,
            'tips_for_teacher': 'Usa listas visuales con colores para cada paso.',
            'tips_for_parent': 'Practica secuencias en actividades cotidianas como preparar el desayuno.',
            'ar_content': {'enabled': False}
        }
    ],

    'hiperactivo': [
        {
            'title': 'Sigue el Ritmo',
            'description': 'Golpea el escritorio siguiendo el ritmo de la música, pero DETENTE cuando la música pare.',
            'activity_type': 'control_impulsos',
            'instructions': '1. Escucha el ritmo de la música\n2. Golpea suavemente cuando suene\n3. Para INMEDIATAMENTE cuando la música se detenga\n4. ¡La clave es el control!',
            'objectives': ['Mejorar control de impulsos', 'Desarrollar autoregulación'],
            'difficulty_level': 1,
            'duration_minutes': 5,
            'tips_for_teacher': 'Varía los tiempos de pausa para aumentar la dificultad.',
            'tips_for_parent': 'Juega este juego en casa para practicar la autorregulación.',
            'ar_content': {'enabled': True, 'type': 'markerless', 'description': 'Visualizador de ritmo en 3D'}
        },
        {
            'title': 'Semáforo de Emociones',
            'description': 'Identifica tu emoción y aplica la técnica del semáforo antes de actuar.',
            'activity_type': 'control_impulsos',
            'instructions': '1. Rojo: PARA y respira 3 veces\n2. Amarillo: PIENSA en tus opciones\n3. Verde: ACTÚA con calma\n4. Practica con situaciones del juego',
            'objectives': ['Control de impulsos', 'Reconocimiento emocional'],
            'difficulty_level': 1,
            'duration_minutes': 8,
            'tips_for_teacher': 'Usa tarjetas físicas de colores para reforzar la actividad.',
            'tips_for_parent': 'Practica el semáforo en situaciones de conflicto en casa.',
            'ar_content': {'enabled': True, 'type': 'marker', 'description': 'Semáforo 3D interactivo'}
        },
        {
            'title': 'Misión Energía Controlada',
            'description': 'Realiza movimientos físicos específicos en momentos precisos para ganar puntos.',
            'activity_type': 'control_impulsos',
            'instructions': '1. Cuando aparezca ★: salta\n2. Cuando aparezca ■: siéntate\n3. Cuando aparezca ●: quédate quieto\n4. ¡Controla tu cuerpo!',
            'objectives': ['Canalizar energía', 'Mejorar inhibición motora'],
            'difficulty_level': 2,
            'duration_minutes': 10,
            'tips_for_teacher': 'Asegura espacio físico suficiente en el aula.',
            'tips_for_parent': 'Ideal para realizarlo en casa con espacio libre.',
            'ar_content': {'enabled': False}
        }
    ],

    'combinado': [
        {
            'title': 'Misión Espacial Organizada',
            'description': 'Organiza una nave espacial completando tareas en orden, con control de impulsos.',
            'activity_type': 'mixta',
            'instructions': '1. Lee TODAS las tareas antes de empezar\n2. Organiza los elementos según el orden correcto\n3. Si quieres hacer algo diferente, PARA y piensa\n4. ¡Completa la misión!',
            'objectives': ['Mejora organización y control de impulsos', 'Desarrolla planificación'],
            'difficulty_level': 2,
            'duration_minutes': 12,
            'tips_for_teacher': 'Divide la actividad en fases cortas con feedback inmediato.',
            'tips_for_parent': 'Celebra cada pequeño logro para mantener la motivación.',
            'ar_content': {'enabled': True, 'type': 'markerless', 'description': 'Nave espacial interactiva en AR'}
        },
        {
            'title': 'Detective de Palabras',
            'description': 'Encuentra palabras ocultas en una sopa de letras sin marcar las incorrectas.',
            'activity_type': 'mixta',
            'instructions': '1. Lee la lista de palabras a encontrar\n2. Busca cada una con calma\n3. SOLO marca cuando estés seguro\n4. Piensa antes de actuar',
            'objectives': ['Atención sostenida', 'Inhibición de respuestas impulsivas'],
            'difficulty_level': 2,
            'duration_minutes': 10,
            'tips_for_teacher': 'Usa palabras relacionadas con temas que le gusten al estudiante.',
            'tips_for_parent': 'Puedes usar sopas de letras en papel también.',
            'ar_content': {'enabled': False}
        },
        {
            'title': 'Constructor de Historias',
            'description': 'Crea una historia corta organizando imágenes en secuencia lógica.',
            'activity_type': 'mixta',
            'instructions': '1. Observa todas las imágenes disponibles\n2. Decide el orden que tenga más sentido\n3. Arrastra las imágenes al orden correcto\n4. ¡Cuéntanos tu historia!',
            'objectives': ['Secuenciación y planificación', 'Atención y creatividad'],
            'difficulty_level': 3,
            'duration_minutes': 15,
            'tips_for_teacher': 'Permite que el estudiante explique su secuencia oralmente.',
            'tips_for_parent': 'Usa fotos familiares para hacer la actividad más significativa.',
            'ar_content': {'enabled': False}
        }
    ],

    'typical': [
        {
            'title': 'Desafío de Memoria',
            'description': 'Memoriza y repite secuencias de colores crecientes.',
            'activity_type': 'memoria',
            'instructions': '1. Observa la secuencia de colores\n2. Repite el orden exacto\n3. Cada nivel agrega un color más',
            'objectives': ['Memoria de trabajo', 'Concentración'],
            'difficulty_level': 2,
            'duration_minutes': 8,
            'tips_for_teacher': 'Aumenta la velocidad de presentación para mayor desafío.',
            'tips_for_parent': 'Juega con cartas de memoria en casa.',
            'ar_content': {'enabled': True, 'type': 'markerless', 'description': 'Secuencia de esferas de colores'}
        }
    ]
}


# ══════════════════════════════════════════════════════════════════
#  CLASE PRINCIPAL
# ══════════════════════════════════════════════════════════════════

class AIActivityGenerator:
    """
    Genera actividades educativas personalizadas para estudiantes con TDAH.

    - Con OPENAI_API_KEY: usa GPT para generar actividades únicas
    - Sin API key: usa el banco de actividades predefinidas
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.model = 'gpt-4o-mini'
        self._client = None

    def _get_client(self):
        """Inicializa el cliente de OpenAI de forma lazy."""
        if self._client is None and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                pass
        return self._client

    # ── PUBLIC API ────────────────────────────────────────────────

    def generate_activity(self, student_profile: Dict, session_data: Dict = None) -> Dict:
        """
        Genera una actividad personalizada para el estudiante.

        Args:
            student_profile: {tdah_type, age, difficulty_level, username}
            session_data: {attention_score, completion_time, difficulties} (opcional)

        Returns:
            Dict con la actividad generada
        """
        client = self._get_client()

        if client:
            return self._generate_with_openai(student_profile, session_data, client)
        else:
            return self._generate_from_bank(student_profile, session_data)

    def generate_recommendations(self, session_results: List[Dict]) -> Dict:
        """
        Genera recomendaciones basadas en múltiples sesiones.

        Args:
            session_results: Lista de resultados de sesiones previas

        Returns:
            Dict con recomendaciones estructuradas
        """
        client = self._get_client()

        if client and session_results:
            return self._recommendations_with_openai(session_results, client)
        else:
            return self._recommendations_fallback(session_results)

    def get_activities_for_type(self, tdah_type: str, count: int = 3) -> List[Dict]:
        """
        Devuelve N actividades del banco para el tipo de TDAH dado.
        Útil para mostrar opciones al profesor.
        """
        bank = ACTIVITIES_BANK.get(tdah_type, ACTIVITIES_BANK['combinado'])
        selected = random.sample(bank, min(count, len(bank)))
        for act in selected:
            act['generated_by'] = 'bank'
        return selected

    # ── OPENAI GENERATION ─────────────────────────────────────────

    def _generate_with_openai(self, student_profile: Dict,
                               session_data: Dict, client) -> Dict:
        """Genera actividad usando GPT."""
        try:
            tdah_type = student_profile.get('tdah_type', 'combinado')
            age = student_profile.get('age', 9)
            difficulty = student_profile.get('difficulty_level', 2)
            username = student_profile.get('username', 'Estudiante')

            attention = session_data.get('attention_score', 70) if session_data else 70

            system_prompt = """Eres un psicopedagogo experto en TDAH infantil.
Generas actividades educativas personalizadas para niños con TDAH.
Respondes SOLO en JSON válido, sin texto adicional ni backticks."""

            user_prompt = f"""Crea UNA actividad educativa para:
- Nombre: {username}
- Subtipo TDAH: {tdah_type}
- Edad: {age} años
- Nivel dificultad: {difficulty}/5
- Puntuación atención reciente: {attention}%

Responde SOLO con este JSON:
{{
    "title": "Nombre creativo de la actividad",
    "description": "Descripción en 1-2 oraciones",
    "activity_type": "atencion|memoria|organizacion|control_impulsos|mixta",
    "difficulty_level": {difficulty},
    "duration_minutes": 10,
    "instructions": "Paso 1...\\nPaso 2...\\nPaso 3...",
    "objectives": ["objetivo 1", "objetivo 2"],
    "tips_for_teacher": "Consejo específico para el profesor",
    "tips_for_parent": "Consejo para los padres",
    "ar_content": {{"enabled": false}}
}}"""

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            activity = json.loads(content)
            activity['generated_by'] = 'openai'
            return activity

        except Exception as e:
            print(f"⚠️  OpenAI error, usando fallback: {e}")
            return self._generate_from_bank(student_profile, session_data)

    # ── BANK FALLBACK ─────────────────────────────────────────────

    def _generate_from_bank(self, student_profile: Dict,
                             session_data: Dict = None) -> Dict:
        """Selecciona actividad del banco local según el perfil."""
        tdah_type = student_profile.get('tdah_type', 'combinado')
        difficulty = student_profile.get('difficulty_level', 2)

        bank = ACTIVITIES_BANK.get(tdah_type, ACTIVITIES_BANK['combinado'])

        # Filtrar por nivel de dificultad aproximado
        suitable = [a for a in bank if abs(a['difficulty_level'] - difficulty) <= 1]
        if not suitable:
            suitable = bank

        activity = random.choice(suitable).copy()
        activity['generated_by'] = 'bank'
        return activity

    # ── RECOMMENDATIONS ───────────────────────────────────────────

    def _recommendations_with_openai(self, session_results: List[Dict],
                                      client) -> Dict:
        """Genera recomendaciones con OpenAI."""
        try:
            avg_attention = (
                sum(s.get('attention_score', 0) for s in session_results)
                / len(session_results)
            )

            system_prompt = """Eres TeacherGPT, asistente pedagógico experto en TDAH.
Analizas datos de estudiantes y generas reportes profesionales en español.
Respondes SOLO en JSON válido."""

            user_prompt = f"""Genera recomendaciones pedagógicas basadas en:
- Sesiones analizadas: {len(session_results)}
- Promedio de atención: {avg_attention:.1f}%
- Datos recientes: {json.dumps(session_results[-3:], ensure_ascii=False)}

Responde en JSON:
{{
    "strengths": ["fortaleza 1", "fortaleza 2"],
    "areas_for_improvement": ["área 1", "área 2"],
    "suggested_activities": ["actividad 1", "actividad 2"],
    "parent_recommendations": ["consejo 1", "consejo 2"],
    "teacher_strategies": ["estrategia 1", "estrategia 2"],
    "progress_summary": "Resumen del progreso en 2-3 oraciones"
}}"""

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=800,
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"⚠️  OpenAI recommendations error: {e}")
            return self._recommendations_fallback(session_results)

    def _recommendations_fallback(self, session_results: List[Dict]) -> Dict:
        """Recomendaciones predefinidas cuando no hay API."""
        avg_attention = (
            sum(s.get('attention_score', 0) for s in session_results)
            / len(session_results)
        ) if session_results else 0

        if avg_attention >= 70:
            strengths = ['Mantiene atención por períodos sostenidos',
                         'Muestra motivación en las actividades']
            areas = ['Puede aumentar la complejidad de las tareas']
            strategies = ['Introducir actividades más desafiantes',
                          'Fomentar proyectos de largo plazo']
        elif avg_attention >= 50:
            strengths = ['Muestra disposición para aprender',
                         'Participa activamente cuando le interesa el tema']
            areas = ['Atención sostenida en tareas largas',
                     'Reducción de distracciones externas']
            strategies = ['Dividir tareas en bloques de 10 min',
                          'Usar recordatorios visuales de color',
                          'Proporcionar descansos frecuentes']
        else:
            strengths = ['Muestra esfuerzo cuando recibe apoyo',
                         'Responde positivamente al refuerzo inmediato']
            areas = ['Atención sostenida', 'Seguimiento de instrucciones',
                     'Control de impulsos']
            strategies = ['Actividades muy cortas (5-7 min)',
                          'Instrucciones de un solo paso',
                          'Refuerzo positivo inmediato y frecuente',
                          'Ambiente libre de distracciones']

        return {
            'strengths': strengths,
            'areas_for_improvement': areas,
            'suggested_activities': [
                'Juegos de atención visual cortos',
                'Ejercicios de respiración antes de iniciar',
                'Actividades con movimiento físico'
            ],
            'parent_recommendations': [
                'Establecer rutinas consistentes en casa',
                'Crear espacio de estudio sin distracciones',
                'Usar refuerzo positivo y recompensas inmediatas',
                'Limitar tiempo de pantallas antes de estudiar'
            ],
            'teacher_strategies': strategies,
            'progress_summary': (
                f'El estudiante muestra un nivel de atención promedio de '
                f'{avg_attention:.1f}%. '
                + ('Se recomienda mantener el nivel actual y aumentar gradualmente la dificultad.'
                   if avg_attention >= 60 else
                   'Se recomienda trabajar con actividades cortas y refuerzo positivo frecuente.')
            )
        }
