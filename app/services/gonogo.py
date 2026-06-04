from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import json
import random
from app.models.student import Student
from app.models.report import Report
from app import db

gonogo_bp = Blueprint('gonogo', __name__, url_prefix='/gonogo')

# Configuración del test
GONOGO_CONFIG = {
    'total_trials': 40,  # 40 estímulos
    'go_percentage': 70,  # 70% son "GO" (debe responder)
    'stimulus_duration': 1000,  # 1 segundo por estímulo (ms)
    'inter_stimulus_interval': 500,  # 0.5s entre estímulos
    'target_stimulus': 'X',  # Debe responder a X
    'nogo_stimulus': 'O',  # NO debe responder a O
}

# VALORES DE REFERENCIA para Go/No-Go
REFERENCE_VALUES_GONOGO = {
    'typical': {
        'precision_go': (85, 100),  # % aciertos en GO
        'precision_nogo': (85, 100),  # % aciertos en NO-GO (no responder)
        'falsos_positivos': (0, 3),  # Responder cuando no debe
        'tiempo_reaccion_promedio': (300, 600)  # ms
    },
    'inatento': {
        'precision_go': (60, 80),
        'precision_nogo': (70, 90),
        'falsos_positivos': (2, 6),
        'tiempo_reaccion_promedio': (500, 900)
    },
    'hiperactivo': {
        'precision_go': (75, 95),
        'precision_nogo': (40, 70),  # Muchos falsos positivos (impulsividad)
        'falsos_positivos': (8, 20),
        'tiempo_reaccion_promedio': (200, 400)  # Muy rápido
    },
    'combinado': {
        'precision_go': (55, 75),
        'precision_nogo': (50, 75),
        'falsos_positivos': (5, 12),
        'tiempo_reaccion_promedio': (400, 700)
    }
}

class GoNoGoTestSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.start_time = datetime.now()
        self.trials = []
        self.metricas = {
            'total_go': 0,
            'total_nogo': 0,
            'aciertos_go': 0,
            'aciertos_nogo': 0,
            'errores_omision': 0,  # No responder cuando debe (GO)
            'falsos_positivos': 0,  # Responder cuando NO debe (NO-GO)
            'precision_go': 0,
            'precision_nogo': 0,
            'tiempo_reaccion_promedio': 0,
            'tiempos_reaccion_go': [],
            'anticipaciones': 0  # Respuestas < 200ms (demasiado rápido)
        }
    
    def agregar_trial(self, trial_data):
        """Agrega un intento al test"""
        self.trials.append(trial_data)
    
    def analizar_resultados(self):
        """Analiza los resultados del Go/No-Go Test"""
        if len(self.trials) < 15:
            return None
        
        print(f"\n{'='*60}")
        print(f"🎮 ANÁLISIS DE TEST GO/NO-GO")
        print(f"{'='*60}")
        
        # Separar trials GO y NO-GO
        go_trials = [t for t in self.trials if t['tipo'] == 'go']
        nogo_trials = [t for t in self.trials if t['tipo'] == 'nogo']
        
        self.metricas['total_go'] = len(go_trials)
        self.metricas['total_nogo'] = len(nogo_trials)
        
        # Análisis de GO trials (debe responder)
        self.metricas['aciertos_go'] = sum(1 for t in go_trials if t['respondio'])
        self.metricas['errores_omision'] = sum(1 for t in go_trials if not t['respondio'])
        
        # Análisis de NO-GO trials (NO debe responder)
        self.metricas['aciertos_nogo'] = sum(1 for t in nogo_trials if not t['respondio'])
        self.metricas['falsos_positivos'] = sum(1 for t in nogo_trials if t['respondio'])
        
        # Precisión
        self.metricas['precision_go'] = (self.metricas['aciertos_go'] / self.metricas['total_go'] * 100) if self.metricas['total_go'] > 0 else 0
        self.metricas['precision_nogo'] = (self.metricas['aciertos_nogo'] / self.metricas['total_nogo'] * 100) if self.metricas['total_nogo'] > 0 else 0
        
        # Tiempos de reacción (solo GO respondidos)
        tiempos_go = [t['tiempo_reaccion'] for t in go_trials if t['respondio'] and t['tiempo_reaccion'] is not None]
        self.metricas['tiempos_reaccion_go'] = tiempos_go
        self.metricas['tiempo_reaccion_promedio'] = sum(tiempos_go) / len(tiempos_go) if tiempos_go else 0
        
        # Anticipaciones (respuestas muy rápidas < 200ms, indica impulsividad)
        self.metricas['anticipaciones'] = sum(1 for t in tiempos_go if t < 200)
        
        print(f"📊 Métricas:")
        print(f"   • GO: {self.metricas['aciertos_go']}/{self.metricas['total_go']} ({self.metricas['precision_go']:.1f}%)")
        print(f"   • NO-GO: {self.metricas['aciertos_nogo']}/{self.metricas['total_nogo']} ({self.metricas['precision_nogo']:.1f}%)")
        print(f"   • Falsos positivos: {self.metricas['falsos_positivos']}")
        print(f"   • Tiempo promedio: {self.metricas['tiempo_reaccion_promedio']:.0f}ms")
        print(f"   • Anticipaciones: {self.metricas['anticipaciones']}")
        
        # Calcular scores detallados
        scores_detallados = self._calcular_scores_detallados()
        
        # Determinar tipo predominante
        tipo_tdah = max(scores_detallados.items(), key=lambda x: x[1]['probabilidad'])[0]
        confianza = scores_detallados[tipo_tdah]['probabilidad']
        
        print(f"\n✅ Tipo detectado: {tipo_tdah} ({confianza:.1f}%)")
        print(f"{'='*60}\n")
        
        return {
            'tipo_tdah': tipo_tdah,
            'confianza': int(confianza),
            'metricas': {k: v for k, v in self.metricas.items() if k != 'tiempos_reaccion_go'},
            'scores_detallados': scores_detallados,
            'duracion': (datetime.now() - self.start_time).seconds
        }
    
    def _calcular_scores_detallados(self):
        """Calcula probabilidad para cada tipo de TDAH"""
        scores = {}
        
        for tipo, rangos in REFERENCE_VALUES_GONOGO.items():
            probabilidad = 0
            detalles = {}
            
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
            
            probabilidad = probabilidad / len(rangos)
            
            scores[tipo] = {
                'probabilidad': round(probabilidad, 1),
                'detalles': detalles,
                'severidad': self._calcular_severidad(probabilidad)
            }
        
        return scores
    
    def _calcular_severidad(self, probabilidad):
        """Determina severidad"""
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


# Almacenamiento de sesiones
test_sessions = {}


@gonogo_bp.route('/')
@login_required
def index():
    """Página principal del Go/No-Go Test"""
    if current_user.role != 'student':
        flash('Solo los estudiantes pueden realizar esta prueba', 'warning')
        return redirect(url_for('auth.dashboard'))
    
    return render_template('student/test_gonogo.html', config=GONOGO_CONFIG)


@gonogo_bp.route('/start_test', methods=['POST'])
@login_required
def start_test():
    """Inicia nueva sesión de Go/No-Go"""
    session_id = f"{current_user.id}_{datetime.now().timestamp()}"
    test_sessions[session_id] = GoNoGoTestSession(current_user.id)
    
    # Generar secuencia de estímulos
    num_go = int(GONOGO_CONFIG['total_trials'] * GONOGO_CONFIG['go_percentage'] / 100)
    num_nogo = GONOGO_CONFIG['total_trials'] - num_go
    
    sequence = ['go'] * num_go + ['nogo'] * num_nogo
    random.shuffle(sequence)
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'config': GONOGO_CONFIG,
        'sequence': sequence
    })


@gonogo_bp.route('/submit_trial', methods=['POST'])
@login_required
def submit_trial():
    """Guarda un intento individual"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in test_sessions:
            return jsonify({'success': False, 'message': 'Sesión inválida'})
        
        session = test_sessions[session_id]
        session.agregar_trial({
            'tipo': data.get('tipo'),  # 'go' o 'nogo'
            'respondio': data.get('respondio'),
            'tiempo_reaccion': data.get('tiempo_reaccion')
        })
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@gonogo_bp.route('/finish_test', methods=['POST'])
@login_required
def finish_test():
    """Finaliza el test y guarda resultados"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in test_sessions:
            return jsonify({'success': False, 'message': 'Sesión no encontrada'})
        
        session = test_sessions[session_id]
        resultado = session.analizar_resultados()
        
        if not resultado:
            return jsonify({'success': False, 'message': 'Datos insuficientes'})
        
        # Guardar en base de datos
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            report = Report(
                student_id=student.id,
                report_type='gonogo_test',
                content=json.dumps(resultado, ensure_ascii=False),
                recommendations=f"Tipo: {resultado['tipo_tdah']} ({resultado['confianza']}%)"
            )
            db.session.add(report)
            db.session.commit()
            
            # ⭐ Recalcular tipo TDAH automáticamente
            print(f"🔄 Recalculando tipo de TDAH automáticamente...")
            resultado_tdah = student.calcular_tipo_tdah()
            
            if resultado_tdah and resultado_tdah['tipo']:
                db.session.commit()
                print(f"✅ Tipo de TDAH actualizado: {resultado_tdah['tipo']} ({resultado_tdah['confianza']:.1f}%)")
            else:
                print(f"ℹ️  Tipo de TDAH no actualizado (insuficientes datos o baja confianza)")
            
            # ⭐ NUEVO: Notificar a los padres
            try:
                from app.models.notification import Notification
                notifications_sent = Notification.notify_parents_of_student(
                    student_id=student.id,
                    title="Test Go/No-Go Completado",
                    message=f"Tu hijo/a ha completado un test Go/No-Go. Clasificación: {resultado['tipo_tdah']} ({resultado['confianza']}%)",
                    notification_type='test_completed'
                )
                if notifications_sent > 0:
                    print(f"📧 Notificados {notifications_sent} padre(s)")
            except Exception as e:
                print(f"⚠️  Error al notificar padres: {e}")
        
        del test_sessions[session_id]
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('gonogo.results',
                                   tipo_tdah=resultado['tipo_tdah'],
                                   confianza=resultado['confianza'],
                                   metricas=json.dumps(resultado['metricas']),
                                   scores=json.dumps(resultado['scores_detallados']))
        })
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@gonogo_bp.route('/results')
@login_required
def results():
    """Muestra resultados del Go/No-Go Test"""
    tipo_tdah = request.args.get('tipo_tdah')
    confianza = request.args.get('confianza', 0, type=int)
    metricas = json.loads(request.args.get('metricas', '{}'))
    scores = json.loads(request.args.get('scores', '{}'))
    
    return render_template('student/resultado_gonogo.html',
                         tipo_tdah=tipo_tdah,
                         confianza=confianza,
                         metricas=metricas,
                         scores_detallados=scores)