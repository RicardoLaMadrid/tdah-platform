"""
app/reports/ai_generator.py

Generador de actividades personalizadas para estudiantes con TDAH.
Usa el banco de actividades local (fallback sin dependencias externas).
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
    Intenta Claude primero; cae al banco local si la API no está disponible.
    """

    def __init__(self, api_key: Optional[str] = None):
        # api_key mantenido por compatibilidad con llamadas existentes, no se usa
        self._client = None

    def _get_client(self):
        return None

    # ── PUBLIC API ────────────────────────────────────────────────

    def generate_activity(self, student_profile: Dict, session_data: Dict = None) -> Dict:
        """
        Genera una actividad personalizada para el estudiante.
        Intenta Claude primero; usa banco local como fallback.

        Args:
            student_profile: {tdah_type, age, difficulty_level, username}
            session_data: {attention_score, completion_time, difficulties} (opcional)

        Returns:
            Dict con la actividad generada
        """
        try:
            return self._generate_with_claude(student_profile, session_data)
        except Exception as e:
            try:
                from flask import current_app
                current_app.logger.warning(f"Claude no disponible para actividad ({e}), usando banco local")
            except RuntimeError:
                pass
            return self._generate_from_bank(student_profile, session_data)

    def _generate_with_claude(self, student_profile: Dict, session_data: Dict = None) -> Dict:
        """Genera actividad usando Claude. Lanza excepción si falla."""
        from app.reports.ai_service import ai_service

        tdah_type = student_profile.get('tdah_type') or 'combinado'
        difficulty = int(student_profile.get('difficulty_level', 2))
        age = student_profile.get('age') or 10

        system_prompt = (
            "Eres un especialista en diseño de actividades educativas para niños "
            "con TDAH (9-12 años) en escuelas bolivianas. Generás UNA actividad "
            "concreta, aplicable en aula, con materiales comunes (papel, lápiz, "
            "tarjetas). Duración: 15-30 minutos. Lenguaje claro para el profesor. "
            "NUNCA sugerís medicación. Respondés SIEMPRE en español latinoamericano."
        )

        context = ""
        if session_data and session_data.get('attention_score'):
            context = f"\nNota: en la última sesión el alumno tuvo {session_data['attention_score']:.0f}% de atención."

        user_prompt = f"""Diseñá una actividad educativa para este perfil:
- Tipo TDAH: {tdah_type}
- Edad: {age} años
- Nivel de dificultad deseado: {difficulty}/5{context}

Respondé con este JSON exacto (sin texto adicional, sin bloques markdown):
{{
  "title": "nombre atractivo de la actividad",
  "description": "1-2 oraciones que describan el propósito",
  "activity_type": "atencion|memoria|organizacion|control_impulsos|mixta",
  "difficulty_level": {difficulty},
  "instructions": "pasos numerados que el profesor debe seguir",
  "ar_content": {{"enabled": false}}
}}"""

        result = ai_service.chat_json(system_prompt, user_prompt, temperature=0.5, max_tokens=600)

        for field in ('title', 'description', 'activity_type', 'instructions'):
            if not result.get(field):
                raise ValueError(f"Claude omitió el campo requerido '{field}'")

        result['difficulty_level'] = int(result.get('difficulty_level', difficulty))
        result.setdefault('ar_content', {'enabled': False})
        result['generated_by'] = 'claude'
        return result

    def generate_recommendations(self, session_results: List[Dict]) -> Dict:
        """
        Genera recomendaciones basadas en múltiples sesiones.

        Args:
            session_results: Lista de resultados de sesiones previas

        Returns:
            Dict con recomendaciones estructuradas
        """
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

    # ── BANK GENERATION ───────────────────────────────────────────

    # ── BANK FALLBACK ─────────────────────────────────────────────

    def _generate_from_bank(self, student_profile: Dict,
                             session_data: Dict = None) -> Dict:
        """Selecciona actividad del banco local según el perfil."""
        tdah_type = student_profile.get('tdah_type', 'combinado')
        difficulty = int(student_profile.get('difficulty_level', 2))

        bank = ACTIVITIES_BANK.get(tdah_type, ACTIVITIES_BANK['combinado'])

        # Filtrar por nivel de dificultad aproximado
        suitable = [a for a in bank if abs(a['difficulty_level'] - difficulty) <= 1]
        if not suitable:
            suitable = bank

        activity = random.choice(suitable).copy()
        activity['generated_by'] = 'bank'
        return activity

    # ── RECOMMENDATIONS ───────────────────────────────────────────

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
