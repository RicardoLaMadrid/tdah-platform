from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import cv2
import numpy as np
import base64
from io import BytesIO
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import json
import os
from app.models.student import Student
from app.models.report import Report
from app.extensions import db
from sqlalchemy import desc

vision_bp = Blueprint('vision', __name__, url_prefix='/vision')

# Cargamos los clasificadores Haar
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# NOTA: el test de visión mantiene estado en memoria por diseño —
# el heatmap numpy (480×640 float32, ~1.2MB) y eye_positions (~900 frames)
# no son serializables a JSON/BD sin refactorizar el motor de CV.
# Si el servidor se reinicia durante un test, el alumno verá un error
# amigable y podrá reiniciar. Aceptable para la demo de defensa.
test_sessions = {}

# VALORES DE REFERENCIA
REFERENCE_VALUES = {
    'typical': {
        'atencion_central': (75, 95),
        'dispersion': (10, 25),
        'precision_seguimiento': (70, 95),
        'reaccion_promedio': (0.3, 0.8)
    },
    'inatento': {
        'atencion_central': (40, 70),
        'dispersion': (15, 35),
        'precision_seguimiento': (40, 65),
        'reaccion_promedio': (0.8, 1.5)
    },
    'hiperactivo': {
        'atencion_central': (50, 75),
        'dispersion': (35, 70),
        'precision_seguimiento': (50, 70),
        'reaccion_promedio': (0.2, 0.5)
    },
    'combinado': {
        'atencion_central': (30, 60),
        'dispersion': (30, 60),
        'precision_seguimiento': (35, 60),
        'reaccion_promedio': (0.5, 1.2)
    }
}

# SECUENCIA DE PUNTOS (posiciones en porcentaje de pantalla)
POINT_SEQUENCE = [
    {'x': 50, 'y': 50, 'color': '#FF0000', 'name': 'Centro'},       # Centro - ROJO
    {'x': 20, 'y': 20, 'color': '#00FF00', 'name': 'Superior Izq'}, # Esquina sup izq - VERDE
    {'x': 80, 'y': 20, 'color': '#0000FF', 'name': 'Superior Der'}, # Esquina sup der - AZUL
    {'x': 50, 'y': 50, 'color': '#FFFF00', 'name': 'Centro'},       # Centro - AMARILLO
    {'x': 20, 'y': 80, 'color': '#FF00FF', 'name': 'Inferior Izq'}, # Esquina inf izq - MAGENTA
    {'x': 80, 'y': 80, 'color': '#00FFFF', 'name': 'Inferior Der'}, # Esquina inf der - CYAN
    {'x': 50, 'y': 50, 'color': '#FFA500', 'name': 'Centro'},       # Centro - NARANJA
    {'x': 50, 'y': 20, 'color': '#800080', 'name': 'Superior'},     # Arriba centro - MORADO
    {'x': 50, 'y': 80, 'color': '#008080', 'name': 'Inferior'},     # Abajo centro - TURQUESA
    {'x': 50, 'y': 50, 'color': '#FF6B6B', 'name': 'Centro Final'}, # Centro final
]

class VisionTestSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.frames_captured = 0
        self.eye_positions = []
        self.gaze_dispersion = []
        self.current_point_index = 0
        self.point_history = []  # Historial de aciertos por punto
        self.current_point_start = None
        self.start_time = datetime.now()
        self.heatmap = None
        self.face_region = None  # Para calibración
        
    def get_current_target(self):
        """Obtiene el punto objetivo actual"""
        if self.current_point_index < len(POINT_SEQUENCE):
            return POINT_SEQUENCE[self.current_point_index]
        return POINT_SEQUENCE[-1]  # Último punto si se acabó la secuencia
    
    def advance_to_next_point(self):
        """Avanza al siguiente punto en la secuencia"""
        if self.current_point_index < len(POINT_SEQUENCE) - 1:
            self.current_point_index += 1
            self.current_point_start = datetime.now()
            return True
        return False
    
    def process_frame(self, image, frame_width, frame_height):
        """Procesa cada frame capturado con detección de dirección de mirada"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if self.heatmap is None:
            self.heatmap = np.zeros((frame_height, frame_width), dtype=np.float32)
        
        # Detectar rostro
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return {'success': False, 'message': 'No se detectó rostro'}
        
        # Usar la cara más grande
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        
        # Guardar región facial para calibración
        if self.face_region is None:
            self.face_region = {'x': x, 'y': y, 'w': w, 'h': h}
        
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = image[y:y+h, x:x+w]
        
        # Detectar ojos
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(20, 20))
        
        if len(eyes) >= 2:
            # Ordenar ojos por posición X (izquierdo y derecho)
            eyes_sorted = sorted(eyes[:2], key=lambda e: e[0])
            
            eye_centers = []
            pupil_positions = []
            
            for (ex, ey, ew, eh) in eyes_sorted:
                # Centro del ojo en coordenadas de pantalla
                eye_center_x = x + ex + ew // 2
                eye_center_y = y + ey + eh // 2
                eye_centers.append((eye_center_x, eye_center_y))
                
                # Intentar detectar pupila (región más oscura del ojo)
                eye_roi = roi_gray[ey:ey+eh, ex:ex+ew]
                
                # Aplicar threshold para encontrar la pupila
                _, threshold = cv2.threshold(eye_roi, 50, 255, cv2.THRESH_BINARY_INV)
                
                # Encontrar contornos
                contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # La pupila suele ser el contorno más grande
                    largest_contour = max(contours, key=cv2.contourArea)
                    M = cv2.moments(largest_contour)
                    
                    if M["m00"] != 0:
                        # Posición de la pupila relativa al ojo
                        pupil_x = int(M["m10"] / M["m00"])
                        pupil_y = int(M["m01"] / M["m00"])
                        
                        # Convertir a coordenadas de pantalla
                        pupil_screen_x = x + ex + pupil_x
                        pupil_screen_y = y + ey + pupil_y
                        pupil_positions.append((pupil_screen_x, pupil_screen_y))
                    else:
                        pupil_positions.append(eye_centers[-1])
                else:
                    pupil_positions.append(eye_centers[-1])
                
                # Actualizar heatmap con posición estimada de mirada
                if len(pupil_positions) > 0:
                    gaze_x, gaze_y = self._estimate_gaze_point(
                        eye_centers[-1], pupil_positions[-1], 
                        frame_width, frame_height
                    )
                    if 0 <= gaze_x < frame_width and 0 <= gaze_y < frame_height:
                        self.heatmap[int(gaze_y), int(gaze_x)] += 1
            
            self.eye_positions.append({
                'eye_centers': eye_centers,
                'pupil_positions': pupil_positions,
                'timestamp': datetime.now()
            })
            
            # Calcular dispersión
            if len(self.eye_positions) > 1:
                prev_pos = self.eye_positions[-2]['eye_centers'][0]
                curr_pos = eye_centers[0]
                dispersion = np.sqrt((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)
                self.gaze_dispersion.append(dispersion)
            
            # Verificar si está mirando al punto objetivo actual
            target = self.get_current_target()
            target_x = frame_width * target['x'] / 100
            target_y = frame_height * target['y'] / 100
            
            # Estimar punto de mirada
            if len(pupil_positions) >= 2:
                avg_gaze_x, avg_gaze_y = self._estimate_gaze_point(
                    ((eye_centers[0][0] + eye_centers[1][0]) / 2,
                     (eye_centers[0][1] + eye_centers[1][1]) / 2),
                    ((pupil_positions[0][0] + pupil_positions[1][0]) / 2,
                     (pupil_positions[0][1] + pupil_positions[1][1]) / 2),
                    frame_width, frame_height
                )
                
                # Distancia al objetivo
                distance_to_target = np.sqrt(
                    (avg_gaze_x - target_x)**2 + 
                    (avg_gaze_y - target_y)**2
                )
                
                # Tolerancia de 150 píxeles (ajustable)
                is_looking_at_target = distance_to_target < 150
                
                # Guardar historial
                self.point_history.append({
                    'point_index': self.current_point_index,
                    'target': target,
                    'gaze_position': (avg_gaze_x, avg_gaze_y),
                    'distance': distance_to_target,
                    'hit': is_looking_at_target,
                    'timestamp': datetime.now()
                })
        
        self.frames_captured += 1
        
        return {
            'success': True, 
            'frames': self.frames_captured,
            'eyes_detected': len(eyes),
            'current_target': self.get_current_target(),
            'current_point_index': self.current_point_index,
            'total_points': len(POINT_SEQUENCE)
        }
    
    def _estimate_gaze_point(self, eye_center, pupil_pos, frame_width, frame_height):
        """Estima el punto de mirada en la pantalla basado en la posición de la pupila"""
        # Vector desde el centro del ojo hasta la pupila
        dx = pupil_pos[0] - eye_center[0]
        dy = pupil_pos[1] - eye_center[1]
        
        # Amplificar el vector (factor de proyección)
        amplification = 3.0
        
        # Punto estimado de mirada
        gaze_x = pupil_pos[0] + dx * amplification
        gaze_y = pupil_pos[1] + dy * amplification
        
        # Limitar a los bordes de la pantalla
        gaze_x = max(0, min(frame_width - 1, gaze_x))
        gaze_y = max(0, min(frame_height - 1, gaze_y))
        
        return gaze_x, gaze_y
    
    def analyze_results(self):
        """Analiza los resultados de la prueba con sistema mejorado"""
        if self.frames_captured < 10:
            return None
        
        # Calcular métricas de seguimiento de puntos
        total_observations = len(self.point_history)
        hits = sum(1 for h in self.point_history if h['hit'])
        precision_seguimiento = (hits / total_observations * 100) if total_observations > 0 else 0
        
        # Calcular tiempo de reacción promedio por punto
        reaction_times = []
        for i in range(len(POINT_SEQUENCE)):
            point_obs = [h for h in self.point_history if h['point_index'] == i]
            if point_obs:
                first_hit = next((h for h in point_obs if h['hit']), None)
                if first_hit and i > 0:
                    # Tiempo desde que cambió el punto
                    prev_point_time = point_obs[0]['timestamp']
                    reaction_time = (first_hit['timestamp'] - prev_point_time).total_seconds()
                    reaction_times.append(reaction_time)
        
        avg_reaction = np.mean(reaction_times) if reaction_times else 0.5
        
        # Dispersión de mirada
        avg_dispersion = np.mean(self.gaze_dispersion) if self.gaze_dispersion else 0
        
        # Calcular atención por zonas
        center_hits = sum(1 for h in self.point_history if h['target']['name'] == 'Centro' and h['hit'])
        center_total = sum(1 for h in self.point_history if h['target']['name'] == 'Centro')
        atencion_central = (center_hits / center_total * 100) if center_total > 0 else 0
        
        metricas = {
            'frames_procesados': self.frames_captured,
            'dispersion_promedio': round(avg_dispersion, 2),
            'atencion_central': round(atencion_central, 2),
            'precision_seguimiento': round(precision_seguimiento, 2),
            'reaccion_promedio': round(avg_reaction, 2),
            'puntos_completados': len(set(h['point_index'] for h in self.point_history)),
            'aciertos_totales': hits,
            'observaciones_totales': total_observations
        }
        
        # Calcular scores para TODOS los tipos
        scores_detallados = self._calcular_scores_detallados(metricas)
        
        # Determinar clasificación primaria
        clasificacion_primaria = max(scores_detallados.items(), key=lambda x: x[1]['probabilidad'])
        tipo_principal = clasificacion_primaria[0]
        
        return {
            'tipo_tdah': tipo_principal,
            'confianza': int(clasificacion_primaria[1]['probabilidad']),
            'scores_detallados': scores_detallados,
            'metricas': metricas,
            'duracion': (datetime.now() - self.start_time).seconds,
            'interpretacion': self._generar_interpretacion(scores_detallados, metricas)
        }
    
    def _calcular_scores_detallados(self, metricas):
        """Calcula probabilidad para CADA tipo incluyendo típico"""
        scores = {}
        
        print(f"\n{'='*60}")
        print(f"🔬 ANÁLISIS DETALLADO DE MÉTRICAS")
        print(f"{'='*60}")
        print(f"📊 Valores medidos:")
        for key, value in metricas.items():
            if key not in ['frames_procesados', 'puntos_completados', 'aciertos_totales', 'observaciones_totales']:
                print(f"   • {key}: {value}")
        
        # Calcular probabilidad para cada tipo
        for tipo, rangos in REFERENCE_VALUES.items():
            probabilidad = 0
            detalles = {}
            
            print(f"\n🎯 Evaluando tipo: {tipo.upper()}")
            
            # Comparar cada métrica con los rangos esperados
            for metrica, (min_val, max_val) in rangos.items():
                valor_actual = metricas.get(metrica, 0)
                
                # Calcular qué tan bien encaja en el rango
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
            
            # Promedio de todos los matches
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
        """Determina nivel de severidad basado en probabilidad"""
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
    
    def _generar_interpretacion(self, scores, metricas):
        """Genera interpretación en lenguaje natural"""
        tipos_ordenados = sorted(scores.items(), key=lambda x: x[1]['probabilidad'], reverse=True)
        principal = tipos_ordenados[0]
        
        interpretaciones = {
            'typical': f"Los patrones observados están dentro del rango típico. Precisión de seguimiento: {metricas['precision_seguimiento']:.1f}%.",
            'inatento': f"Se observan dificultades de atención sostenida. Precisión de seguimiento: {metricas['precision_seguimiento']:.1f}%. Tiempo de reacción: {metricas['reaccion_promedio']:.2f}s.",
            'hiperactivo': f"Movimientos rápidos e impulsivos. Reacción muy rápida ({metricas['reaccion_promedio']:.2f}s) pero con dispersión alta ({metricas['dispersion_promedio']}).",
            'combinado': f"Características mixtas. Precisión: {metricas['precision_seguimiento']:.1f}%, Dispersión: {metricas['dispersion_promedio']}."
        }
        
        return interpretaciones[principal[0]]
    
    def generate_heatmap(self, output_path):
        """Genera la visualización del heatmap"""
        if self.heatmap is None:
            return None
        
        try:
            heatmap_normalized = cv2.normalize(self.heatmap, None, 0, 255, cv2.NORM_MINMAX)
            heatmap_color = cv2.applyColorMap(heatmap_normalized.astype(np.uint8), cv2.COLORMAP_JET)
            
            plt.figure(figsize=(10, 8))
            plt.imshow(cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB))
            plt.title('Mapa de Atención Visual', fontsize=16, fontweight='bold')
            plt.colorbar(label='Intensidad de fijación')
            plt.axis('off')
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return output_path
        except Exception as e:
            print(f"❌ Error generando heatmap: {str(e)}")
            return None


# RUTAS (sin cambios en las firmas)
@vision_bp.route('/')
@login_required
def index():
    """Página principal del test de visión"""
    if current_user.role != 'student':
        flash('Solo los estudiantes pueden realizar esta prueba', 'warning')
        return redirect(url_for('auth.dashboard'))
    
    return render_template('student/test_vision.html')


@vision_bp.route('/start_test', methods=['POST'])
@login_required
def start_test():
    """Inicia una nueva sesión de prueba"""
    session_id = f"{current_user.id}_{datetime.now().timestamp()}"
    test_sessions[session_id] = VisionTestSession(current_user.id)
    
    print(f"🆕 Nueva sesión creada: {session_id}")
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Sesión iniciada correctamente',
        'point_sequence': POINT_SEQUENCE
    })


@vision_bp.route('/process_frame', methods=['POST'])
@login_required
def process_frame():
    """Procesa cada frame capturado durante la prueba"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        image_data = data.get('imageData')
        frame_width = data.get('frameWidth', 640)
        frame_height = data.get('frameHeight', 480)
        
        if not session_id or session_id not in test_sessions:
            return jsonify({'success': False, 'message': 'Sesión expirada. El servidor se reinició — recarga la página y vuelve a iniciar el test.', 'expired': True})
        
        image_data = image_data.split(",")[1]
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        session = test_sessions[session_id]
        result = session.process_frame(image, frame_width, frame_height)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})





@vision_bp.route('/results')
@login_required
def results():
    """Muestra los resultados del test de visión"""
    try:
        tipo_tdah = request.args.get('tipo_tdah')
        confianza = request.args.get('confianza', 0, type=int)
        heatmap_filename = request.args.get('heatmap_filename')
        duracion = request.args.get('duracion', 0, type=int)
        scores_json = request.args.get('scores', '{}')
        metricas_json = request.args.get('metricas', '{}')
        interpretacion = request.args.get('interpretacion', '')
        
        if not tipo_tdah:
            flash('No se encontraron resultados del test', 'warning')
            return redirect(url_for('vision.index'))
        
        scores_detallados = json.loads(scores_json)
        metricas = json.loads(metricas_json)
        
        analysis = {
            'tipo_tdah': tipo_tdah,
            'confianza': confianza,
            'duracion': duracion,
            'scores_detallados': scores_detallados,
            'metricas': metricas,
            'interpretacion': interpretacion
        }
        
        return render_template('student/resultado_vision.html', 
                               analysis=analysis,
                               heatmap_url=f'/static/uploads/heatmaps/{heatmap_filename}')
    except Exception as e:
        print(f"💥 Error en results: {str(e)}")
        flash(f'Error al cargar resultados: {str(e)}', 'danger')
        return redirect(url_for('vision.index'))
    

@vision_bp.route('/finish_test/<session_id>', methods=['POST'])
@login_required
def finish_test(session_id):
    """Finaliza el test y procesa resultados"""
    print(f"🔍 Iniciando finish_test para session_id: {session_id}")
    
    try:
        if session_id not in test_sessions:
            print(f"Sesión de visión {session_id} no encontrada (probable hot-reload)")
            return jsonify({'success': False, 'message': 'Sesión expirada. El servidor se reinició durante el test — inicia el test de nuevo.'})
        
        session = test_sessions[session_id]
        analysis = session.analyze_results()
        
        if not analysis:
            print(f"❌ No hay suficientes datos para análisis")
            return jsonify({
                'success': False, 
                'message': 'No se capturaron suficientes datos para el análisis'
            })
        
        print(f"✅ Análisis completado: {analysis['tipo_tdah']}, confianza: {analysis['confianza']}%")
        
        # Generar heatmap
        heatmap_filename = f'heatmap_{current_user.id}_{int(datetime.now().timestamp())}.png'
        heatmap_dir = os.path.join('app', 'static', 'uploads', 'heatmaps')
        os.makedirs(heatmap_dir, exist_ok=True)
        heatmap_path = os.path.join(heatmap_dir, heatmap_filename)
        session.generate_heatmap(heatmap_path)
        
        # Guardar reporte
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            report = Report(
                student_id=student.id,
                report_type='vision_test',
                content=json.dumps(analysis, ensure_ascii=False),
                recommendations=f"Tipo: {analysis['tipo_tdah']} ({analysis['confianza']}%). {analysis['interpretacion'][:200]}"
            )
            db.session.add(report)
            db.session.commit()  # Commit para que el reporte exista antes de recalcular
            # ⭐ NUEVO: Notificar a los padres
            from app.models.notification import Notification
            Notification.notify_parents_of_student(
                student_id=student.id,
                title=f"Test de Visión Completado",
                message=f"Tu hijo/a ha completado un test de visión. Tipo detectado: {analysis['tipo_tdah']} ({analysis['confianza']}%)",
                notification_type='test_completed'
            )
            
            # ⭐ NUEVO: RECALCULAR TIPO DE TDAH AUTOMÁTICAMENTE
            print(f"🔄 Recalculando tipo de TDAH automáticamente...")
            resultado = student.calcular_tipo_tdah()
            
            if resultado and resultado['tipo']:
                db.session.commit()  # Guardar la actualización
                print(f"✅ Tipo de TDAH actualizado: {resultado['tipo']} ({resultado['confianza']:.1f}%)")
            else:
                print(f"ℹ️  Tipo de TDAH no actualizado (insuficientes datos o baja confianza)")
        
        del test_sessions[session_id]
        
        redirect_url = url_for('vision.results', 
                              tipo_tdah=analysis['tipo_tdah'],
                              confianza=analysis['confianza'],
                              heatmap_filename=heatmap_filename,
                              duracion=analysis['duracion'],
                              scores=json.dumps(analysis['scores_detallados']),
                              metricas=json.dumps(analysis['metricas']),
                              interpretacion=analysis['interpretacion'])
        
        return jsonify({'success': True, 'redirect_url': redirect_url})
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    