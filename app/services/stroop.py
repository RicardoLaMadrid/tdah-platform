from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import json
from app.models.student import Student
from app.models.report import Report
from app import db

stroop_bp = Blueprint('stroop', __name__, url_prefix='/stroop')

# Configuración del test
STROOP_CONFIG = {
    'total_trials': 30,  # 30 intentos
    'time_per_trial': 3000,  # 3 segundos por intento (ms)
    'colors': ['rojo', 'azul', 'verde', 'amarillo', 'morado', 'naranja'],
    'color_codes': {
        'rojo': '#FF0000',
        'azul': '#0000FF',
        'verde': '#00FF00',
        'amarillo': '#FFD700',
        'morado': '#800080',
        'naranja': '#FF8C00'
    }
}

# VALORES DE REFERENCIA para Stroop
REFERENCE_VALUES_STROOP = {
    'typical': {
        'precision': (80, 100),
        'tiempo_promedio': (800, 1500),  # ms
        'errores_incongruentes': (0, 3),
        'efecto_stroop': (100, 300)  # diferencia congruente vs incongruente
    },
    'inatento': {
        'precision': (50, 75),
        'tiempo_promedio': (1500, 2500),
        'errores_incongruentes': (4, 10),
        'efecto_stroop': (300, 600)
    },
    'hiperactivo': {
        'precision': (60, 85),
        'tiempo_promedio': (600, 1200),  # Muy rápido (impulsivo)
        'errores_incongruentes': (5, 12),
        'efecto_stroop': (200, 500)
    },
    'combinado': {
        'precision': (45, 70),
        'tiempo_promedio': (1200, 2200),
        'errores_incongruentes': (6, 15),
        'efecto_stroop': (350, 700)
    }
}

class StroopTestSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.start_time = datetime.now()
        self.trials = []  # Lista de intentos
        self.metricas = {
            'total_intentos': 0,
            'correctos': 0,
            'incorrectos': 0,
            'precision': 0,
            'tiempo_promedio': 0,
            'errores_congruentes': 0,
            'errores_incongruentes': 0,
            'tiempo_congruente': 0,
            'tiempo_incongruente': 0,
            'efecto_stroop': 0
        }
    
    def agregar_trial(self, trial_data):
        """Agrega un intento al test"""
        self.trials.append(trial_data)
    
    def analizar_resultados(self):
        """Analiza los resultados del test Stroop"""
        if len(self.trials) < 10:
            return None
        
        print(f"\n{'='*60}")
        print(f"🎨 ANÁLISIS DE TEST STROOP")
        print(f"{'='*60}")
        
        # Separar trials congruentes e incongruentes
        congruentes = [t for t in self.trials if t['tipo'] == 'congruente']
        incongruentes = [t for t in self.trials if t['tipo'] == 'incongruente']
        
        # Calcular métricas básicas
        self.metricas['total_intentos'] = len(self.trials)
        self.metricas['correctos'] = sum(1 for t in self.trials if t['correcto'])
        self.metricas['incorrectos'] = self.metricas['total_intentos'] - self.metricas['correctos']
        self.metricas['precision'] = (self.metricas['correctos'] / self.metricas['total_intentos'] * 100)
        
        # Tiempos de reacción
        tiempos_validos = [t['tiempo_reaccion'] for t in self.trials if t['correcto']]
        self.metricas['tiempo_promedio'] = sum(tiempos_validos) / len(tiempos_validos) if tiempos_validos else 0
        
        # Errores por tipo
        self.metricas['errores_congruentes'] = sum(1 for t in congruentes if not t['correcto'])
        self.metricas['errores_incongruentes'] = sum(1 for t in incongruentes if not t['correcto'])
        
        # Tiempos por tipo (solo correctos)
        tiempos_congr = [t['tiempo_reaccion'] for t in congruentes if t['correcto']]
        tiempos_incongr = [t['tiempo_reaccion'] for t in incongruentes if t['correcto']]
        
        self.metricas['tiempo_congruente'] = sum(tiempos_congr) / len(tiempos_congr) if tiempos_congr else 0
        self.metricas['tiempo_incongruente'] = sum(tiempos_incongr) / len(tiempos_incongr) if tiempos_incongr else 0
        
        # Efecto Stroop (diferencia de tiempos)
        self.metricas['efecto_stroop'] = self.metricas['tiempo_incongruente'] - self.metricas['tiempo_congruente']
        
        print(f"📊 Métricas:")
        for key, value in self.metricas.items():
            if key not in ['total_intentos']:
                print(f"   • {key}: {value:.2f}")
        
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
            'metricas': self.metricas,
            'scores_detallados': scores_detallados,
            'duracion': (datetime.now() - self.start_time).seconds
        }
    
    def _calcular_scores_detallados(self):
        """Calcula probabilidad para cada tipo de TDAH"""
        scores = {}
        
        for tipo, rangos in REFERENCE_VALUES_STROOP.items():
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


@stroop_bp.route('/')
@login_required
def index():
    """Página principal del Stroop Test"""
    if current_user.role != 'student':
        flash('Solo los estudiantes pueden realizar esta prueba', 'warning')
        return redirect(url_for('auth.dashboard'))
    
    return render_template('student/test_stroop.html', config=STROOP_CONFIG)


@stroop_bp.route('/start_test', methods=['POST'])
@login_required
def start_test():
    """Inicia nueva sesión de Stroop"""
    session_id = f"{current_user.id}_{datetime.now().timestamp()}"
    test_sessions[session_id] = StroopTestSession(current_user.id)
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'config': STROOP_CONFIG
    })


@stroop_bp.route('/submit_trial', methods=['POST'])
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
            'palabra': data.get('palabra'),
            'color': data.get('color'),
            'respuesta': data.get('respuesta'),
            'correcto': data.get('correcto'),
            'tiempo_reaccion': data.get('tiempo_reaccion'),
            'tipo': data.get('tipo')  # 'congruente' o 'incongruente'
        })
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@stroop_bp.route('/finish_test', methods=['POST'])
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
                report_type='stroop_test',
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
                    title="Test de Stroop Completado",
                    message=f"Tu hijo/a ha completado un test de Stroop. Clasificación: {resultado['tipo_tdah']} ({resultado['confianza']}%)",
                    notification_type='test_completed'
                )
                if notifications_sent > 0:
                    print(f"📧 Notificados {notifications_sent} padre(s)")
            except Exception as e:
                print(f"⚠️  Error al notificar padres: {e}")
        
        del test_sessions[session_id]
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('stroop.results',
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


@stroop_bp.route('/results')
@login_required
def results():
    """Muestra resultados del Stroop Test"""
    tipo_tdah = request.args.get('tipo_tdah')
    confianza = request.args.get('confianza', 0, type=int)
    metricas = json.loads(request.args.get('metricas', '{}'))
    scores = json.loads(request.args.get('scores', '{}'))
    
    return render_template('student/resultado_stroop.html',
                         tipo_tdah=tipo_tdah,
                         confianza=confianza,
                         metricas=metricas,
                         scores_detallados=scores)