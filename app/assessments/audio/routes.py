from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import os
import speech_recognition as sr
from pydub import AudioSegment
from datetime import datetime
import json
import numpy as np
from app.models.student import Student
from app.models.report import Report
from app.extensions import db

audio_bp = Blueprint('audio', __name__, url_prefix='/audio')

# Textos para leer según edad/nivel
TEXTOS_LECTURA = {
    'basico': """
    Había una vez un niño llamado Lucas. Lucas siempre tenía muchas ideas y le encantaba soñar despierto. 
    En la escuela, su maestro le decía que prestara más atención, pero a veces su mente se iba a lugares mágicos.
    
    Un día, Lucas decidió explorar un bosque cercano. Mientras caminaba, vio a una ardilla correr rápido de un árbol a otro. 
    Lucas intentó seguirla, pero se distrajo con una mariposa colorida.
    """,
    'intermedio': """
    El viaje hacia el autoconocimiento es fundamental para comprender nuestras fortalezas y debilidades. 
    Muchas personas encuentran difícil mantener la concentración en tareas prolongadas, especialmente cuando 
    hay múltiples estímulos en el ambiente. La capacidad de regular la atención es una habilidad que puede 
    desarrollarse con práctica constante y estrategias adecuadas.
    """,
    'avanzado': """
    La neuroplasticidad cerebral demuestra que nuestro cerebro puede adaptarse y modificar sus conexiones 
    neuronales a lo largo de la vida. Los estudios contemporáneos sobre funciones ejecutivas revelan que 
    la atención sostenida, la memoria de trabajo y el control inhibitorio son componentes fundamentales 
    para el funcionamiento cognitivo óptimo en contextos académicos y sociales.
    """
}

# VALORES DE REFERENCIA mejorados (basados en estudios)
REFERENCE_VALUES_AUDIO = {
    'typical': {
        'precision': (75, 95),
        'velocidad_lectura': (120, 180),  # palabras por minuto
        'repeticiones': (0, 3),
        'fluidez': (70, 95)
    },
    'inatento': {
        'precision': (40, 70),
        'velocidad_lectura': (60, 110),
        'repeticiones': (2, 6),
        'fluidez': (40, 65)
    },
    'hiperactivo': {
        'precision': (60, 80),
        'velocidad_lectura': (180, 250),
        'repeticiones': (4, 10),
        'fluidez': (50, 70)
    },
    'combinado': {
        'precision': (35, 65),
        'velocidad_lectura': (70, 190),
        'repeticiones': (3, 8),
        'fluidez': (35, 60)
    }
}

class AudioTestSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.start_time = datetime.now()
        self.texto_original = ""
        self.transcripcion = ""
        self.metricas = {
            'duracion_grabacion': 0,
            'palabras_correctas': 0,
            'palabras_totales': 0,
            'precision': 0,
            'pausas_detectadas': 0,
            'repeticiones': 0,
            'fluidez': 0,
            'velocidad_lectura': 0
        }
        
    def analizar_audio(self, audio_path, texto_original):
        """Analiza el audio grabado y lo compara con el texto original"""
        self.texto_original = texto_original
        
        try:
            audio_path = self._convertir_audio(audio_path)
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
                
                audio = AudioSegment.from_file(audio_path)
                self.metricas['duracion_grabacion'] = len(audio) / 1000.0
                
                try:
                    self.transcripcion = recognizer.recognize_google(audio_data, language='es-ES')
                except sr.UnknownValueError:
                    return {
                        'success': False,
                        'message': 'No se pudo entender el audio. Por favor, habla más claro y fuerte.'
                    }
                except sr.RequestError as e:
                    return {
                        'success': False,
                        'message': f'Error en el servicio de reconocimiento: {str(e)}'
                    }
            
            self._calcular_metricas()
            
            # ⭐ NUEVO: Sistema mejorado de clasificación
            scores_detallados = self._calcular_scores_detallados()
            
            # Determinar tipo con mayor probabilidad
            tipo_tdah = max(scores_detallados.items(), key=lambda x: x[1]['probabilidad'])[0]
            confianza = scores_detallados[tipo_tdah]['probabilidad']
            
            return {
                'success': True,
                'transcripcion': self.transcripcion,
                'tipo_tdah': tipo_tdah,
                'confianza': int(confianza),
                'metricas': self.metricas,
                'scores_detallados': scores_detallados  # ⭐ NUEVO
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al procesar el audio: {str(e)}'
            }
    
    def _convertir_audio(self, audio_path):
        """Convierte el audio a formato WAV compatible"""
        try:
            if audio_path.lower().endswith('.wav'):
                return audio_path
            
            audio = AudioSegment.from_file(audio_path)
            wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_path, format='wav')
            return wav_path
        except:
            return audio_path
    
    def _calcular_metricas(self):
        """Calcula métricas de lectura comparando transcripción con texto original"""
        palabras_original = self.texto_original.lower().split()
        palabras_transcritas = self.transcripcion.lower().split()
        
        self.metricas['palabras_totales'] = len(palabras_original)
        
        palabras_correctas = 0
        for palabra_original in palabras_original:
            for palabra_transcrita in palabras_transcritas:
                if self._similitud_palabras(palabra_original, palabra_transcrita) > 0.8:
                    palabras_correctas += 1
                    break
        
        self.metricas['palabras_correctas'] = palabras_correctas
        self.metricas['precision'] = (palabras_correctas / len(palabras_original) * 100) if palabras_original else 0
        
        self.metricas['repeticiones'] = len(palabras_transcritas) - len(set(palabras_transcritas))
        
        if self.metricas['duracion_grabacion'] > 0:
            self.metricas['velocidad_lectura'] = (len(palabras_transcritas) / self.metricas['duracion_grabacion']) * 60
        
        velocidad_normal = 150
        factor_velocidad = min(self.metricas['velocidad_lectura'] / velocidad_normal, 1.5)
        factor_precision = self.metricas['precision'] / 100
        self.metricas['fluidez'] = (factor_velocidad * factor_precision) * 100
    
    def _similitud_palabras(self, palabra1, palabra2):
        """Calcula similitud entre dos palabras"""
        if palabra1 == palabra2:
            return 1.0
        
        len1, len2 = len(palabra1), len(palabra2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        comunes = sum(1 for c in palabra1 if c in palabra2)
        return comunes / max(len1, len2)
    
    def _calcular_scores_detallados(self):
        """
        ⭐ NUEVO: Calcula probabilidad para CADA tipo usando rangos de referencia
        Similar al sistema de visión para consistencia
        """
        scores = {}
        
        print(f"\n{'='*60}")
        print(f"🔬 ANÁLISIS DETALLADO DE TEST DE AUDIO")
        print(f"{'='*60}")
        print(f"📊 Métricas medidas:")
        for key in ['precision', 'velocidad_lectura', 'repeticiones', 'fluidez']:
            print(f"   • {key}: {self.metricas[key]}")
        
        for tipo, rangos in REFERENCE_VALUES_AUDIO.items():
            probabilidad = 0
            detalles = {}
            
            print(f"\n🎯 Evaluando tipo: {tipo.upper()}")
            
            for metrica, (min_val, max_val) in rangos.items():
                valor_actual = self.metricas.get(metrica, 0)
                
                if min_val <= valor_actual <= max_val:
                    match = 100
                else:
                    if valor_actual < min_val:
                        distancia = min_val - valor_actual
                        match = max(0, 100 - (distancia / min_val * 100))
                    else:
                        distancia = valor_actual - max_val
                        match = max(0, 100 - (distancia / max_val * 100))
                
                detalles[metrica] = {
                    'valor': valor_actual,
                    'rango_esperado': (min_val, max_val),
                    'match': round(match, 1)
                }
                probabilidad += match
                
                print(f"   • {metrica}: {valor_actual} (esperado: {min_val}-{max_val}) = {match:.1f}% match")
            
            probabilidad = probabilidad / len(rangos)
            
            scores[tipo] = {
                'probabilidad': round(probabilidad, 1),
                'detalles': detalles,
                'severidad': self._calcular_severidad(probabilidad)
            }
            
            print(f"   ✅ Probabilidad total: {probabilidad:.1f}%")
        
        print(f"\n{'='*60}")
        print(f"📈 RESULTADOS FINALES:")
        for tipo, datos in sorted(scores.items(), key=lambda x: x[1]['probabilidad'], reverse=True):
            print(f"   {tipo.upper()}: {datos['probabilidad']}% ({datos['severidad']})")
        print(f"{'='*60}\n")
        
        return scores
    
    def _calcular_severidad(self, probabilidad):
        """Determina nivel de severidad"""
        if probabilidad >= 80:
            return 'Alta'
        elif probabilidad >= 60:
            return 'Moderada-Alta'
        elif probabilidad >= 40:
            return 'Moderada'
        elif probabilidad >= 20:
            return 'Leve'
        else:
            return 'Mínima'


# FIX: estado migrado de dict en memoria (test_sessions) a BD (active_test_sessions)
# para sobrevivir hot-reload del servidor en desarrollo


@audio_bp.route('/')
@login_required
def index():
    """Página principal del test de audio"""
    if current_user.role != 'student':
        flash('Solo los estudiantes pueden realizar esta prueba', 'warning')
        return redirect(url_for('auth.dashboard'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    nivel = 'basico'
    # ⭐ NOTA: El campo 'age' no existe en el modelo actual
    # Usar 'grade' como alternativa
    if student and student.grade:
        try:
            grade_num = int(''.join(filter(str.isdigit, student.grade)))
            if grade_num >= 7:
                nivel = 'avanzado'
            elif grade_num >= 4:
                nivel = 'intermedio'
        except:
            pass
    
    texto_para_leer = TEXTOS_LECTURA[nivel]
    
    return render_template('student/test_audio.html', 
                         texto_para_leer=texto_para_leer,
                         nivel=nivel)


@audio_bp.route('/start_test', methods=['POST'])
@login_required
def start_test():
    """Inicia una nueva sesión de prueba de audio — persiste en BD."""
    from app.core.models.active_test_session import ActiveTestSession

    ActiveTestSession.cleanup_stale('audio')

    session_id = f"{current_user.id}_{datetime.now().timestamp()}"
    ats = ActiveTestSession(
        session_id=session_id,
        test_type='audio',
        user_id=current_user.id,
        data={'start_time': datetime.now().isoformat()},
    )
    db.session.add(ats)
    db.session.commit()

    return jsonify({'success': True, 'session_id': session_id, 'message': 'Sesión iniciada correctamente'})


@audio_bp.route('/upload_audio', methods=['POST'])
@login_required
def upload_audio():
    """Procesa el audio subido"""
    try:
        session_id = request.form.get('session_id')
        nivel = request.form.get('nivel', 'basico')
        
        if 'audio' not in request.files:
            flash('No se recibió ningún archivo de audio', 'danger')
            return redirect(url_for('audio.index'))
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(url_for('audio.index'))
        
        from app.core.models.active_test_session import ActiveTestSession
        ats = ActiveTestSession.query.get(session_id) if session_id else None
        if not ats:
            # Crea sesión de respaldo si el servidor se reinició (sesión perdida)
            session_id = f"{current_user.id}_{datetime.now().timestamp()}"
            ats = ActiveTestSession(
                session_id=session_id,
                test_type='audio',
                user_id=current_user.id,
                data={'start_time': datetime.now().isoformat()},
            )
            db.session.add(ats)
            db.session.commit()

        upload_dir = os.path.join('app', 'static', 'uploads', 'audios')
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"audio_{current_user.id}_{datetime.now().timestamp()}.wav"
        audio_path = os.path.join(upload_dir, filename)
        audio_file.save(audio_path)

        session = AudioTestSession(current_user.id)
        texto_original = TEXTOS_LECTURA[nivel]
        resultado = session.analizar_audio(audio_path, texto_original)
        
        if not resultado['success']:
            flash(resultado['message'], 'danger')
            return redirect(url_for('audio.index'))
        
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            report = Report(
                student_id=student.id,
                report_type='audio_test',
                content=json.dumps({
                    'transcripcion': resultado['transcripcion'],
                    'metricas': resultado['metricas'],
                    'tipo_tdah': resultado['tipo_tdah'],
                    'confianza': resultado['confianza'],
                    'scores_detallados': resultado.get('scores_detallados', {})  # ⭐ NUEVO
                }, ensure_ascii=False),
                recommendations=f"Tipo detectado: {resultado['tipo_tdah']} con {resultado['confianza']}% de confianza"
            )
            db.session.add(report)
            db.session.commit()  # Commit para que exista el reporte
            
            
        # ⭐ NUEVO: Notificar a los padres
            try:
                from app.models.notification import Notification
                notifications_sent = Notification.notify_parents_of_student(
                    student_id=student.id,
                    title="Test de Audio Completado",
                    message=f"Tu hijo/a ha completado un test de audio. Clasificación: {resultado['tipo_tdah']} ({resultado['confianza']}%)",
                    notification_type='test_completed'
                    )
                if notifications_sent > 0:
                    print(f"📧 Notificados {notifications_sent} padre(s)")
            except Exception as e:
                print(f"⚠️  Error al notificar padres: {e}")
            
            # ⭐ NUEVO: RECALCULAR TIPO DE TDAH AUTOMÁTICAMENTE
            print(f"🔄 Recalculando tipo de TDAH automáticamente...")
            resultado_tdah = student.calcular_tipo_tdah()
            
            if resultado_tdah and resultado_tdah['tipo']:
                db.session.commit()
                print(f"✅ Tipo de TDAH actualizado: {resultado_tdah['tipo']} ({resultado_tdah['confianza']:.1f}%)")
            else:
                print(f"ℹ️  Tipo de TDAH no actualizado (insuficientes datos o baja confianza)")
        
        if ats:
            db.session.delete(ats)
            db.session.commit()
        
        return redirect(url_for('audio.results', 
                              tipo_tdah=resultado['tipo_tdah'],
                              confianza=resultado['confianza'],
                              transcripcion=resultado['transcripcion'],
                              metricas=json.dumps(resultado['metricas']),
                              scores=json.dumps(resultado.get('scores_detallados', {}))))  # ⭐ NUEVO
        
    except Exception as e:
        print(f"💥 Error en upload_audio: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error al procesar el audio: {str(e)}', 'danger')
        return redirect(url_for('audio.index'))


@audio_bp.route('/results')
@login_required
def results():
    """Muestra los resultados del test de audio"""
    tipo_tdah = request.args.get('tipo_tdah', 'No determinado')
    confianza = request.args.get('confianza', 0, type=int)
    transcripcion = request.args.get('transcripcion', '')
    metricas = json.loads(request.args.get('metricas', '{}'))
    scores = json.loads(request.args.get('scores', '{}'))  # ⭐ NUEVO
    
    return render_template('student/resultado_audio.html',
                         tipo_tdah=tipo_tdah,
                         confianza=confianza,
                         transcripcion=transcripcion,
                         metricas=metricas,
                         scores_detallados=scores)  # ⭐ NUEVO