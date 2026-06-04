from app.extensions import db
from datetime import datetime
from sqlalchemy import desc
import json

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # ⭐ NUEVOS — Datos personales del alumno
    full_name = db.Column(db.String(200))
    national_id = db.Column(db.String(50))  # Cédula de identidad
    
    # Académicos
    grade = db.Column(db.String(50))
    section = db.Column(db.String(50))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    age = db.Column(db.Integer)
    
    # ⭐ NUEVOS — Información médica
    allergies = db.Column(db.Text)
    medical_conditions = db.Column(db.Text)
    medications = db.Column(db.Text)
    
    # ⭐ NUEVOS — Dirección y emergencia
    address = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(200))
    emergency_contact_phone = db.Column(db.String(20))
    
    # TDAH (existente)
    tdah_type = db.Column(db.String(50))
    tdah_confidence = db.Column(db.Float, default=0)
    last_evaluation_date = db.Column(db.DateTime)
    
    # Metadata
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        backref=db.backref('student_profile', lazy='dynamic')
    )
    teacher = db.relationship(
        'User',
        foreign_keys=[teacher_id],
        backref=db.backref('students_assigned', lazy='dynamic')
    )
    activities = db.relationship('Activity', backref='student', lazy='dynamic')
    sessions = db.relationship('Session', backref='student', lazy='dynamic')
    reports = db.relationship('Report', backref='student', lazy='dynamic')
    
    def __repr__(self):
        return f'<Student {self.user.username}>'
    
    def calcular_tipo_tdah(self):
        """
        Calcula automáticamente el tipo de TDAH basado en los últimos tests.
        Usa un algoritmo de consenso ponderado por tiempo.
        """
        from app.models.report import Report
        from flask import current_app
        
        print(f"\n{'='*60}")
        print(f"🔬 CALCULANDO TIPO TDAH PARA ESTUDIANTE {self.id}")
        print(f"{'='*60}")
        
        # Obtener últimos 3 tests de cada tipo
        vision_reports = Report.query.filter_by(
            student_id=self.id, report_type='vision_test'
        ).order_by(desc(Report.created_at)).limit(3).all()
        
        audio_reports = Report.query.filter_by(
            student_id=self.id, report_type='audio_test'
        ).order_by(desc(Report.created_at)).limit(3).all()
        
        stroop_reports = Report.query.filter_by(
            student_id=self.id, report_type='stroop_test'
        ).order_by(desc(Report.created_at)).limit(3).all()
        
        gonogo_reports = Report.query.filter_by(
            student_id=self.id, report_type='gonogo_test'
        ).order_by(desc(Report.created_at)).limit(3).all()
        
        print(f"📊 Tests encontrados:")
        print(f"   • Visión: {len(vision_reports)}")
        print(f"   • Audio: {len(audio_reports)}")
        print(f"   • Stroop: {len(stroop_reports)}")
        print(f"   • Go/No-Go: {len(gonogo_reports)}")
        
        # ⭐ ESTA LÍNEA ES LA QUE FALTABA
        total_tests = len(vision_reports) + len(audio_reports) + len(stroop_reports) + len(gonogo_reports)
        
        min_tests = current_app.config.get('TDAH_MIN_TESTS', 2)
        if total_tests < min_tests:
            print(f"⚠️  Insuficientes tests ({total_tests}/{min_tests} mínimo)")
            print(f"{'='*60}\n")
            return None
        
        # Extraer datos de cada tipo de test
        def extract_data(reports):
            data = []
            for report in reports:
                try:
                    content = json.loads(report.content)
                    data.append({
                        'tipo': content.get('tipo_tdah'),
                        'confianza': content.get('confianza', 0),
                        'fecha': report.created_at
                    })
                except:
                    continue
            return data
        
        vision_data = extract_data(vision_reports)
        audio_data = extract_data(audio_reports)
        stroop_data = extract_data(stroop_reports)
        gonogo_data = extract_data(gonogo_reports)
        
        # Aplicar algoritmo de consenso
        tipo_final, confianza_final = self._algoritmo_consenso(
            vision_data, audio_data, stroop_data, gonogo_data
        )
        
        if tipo_final:
            print(f"\n✅ RESULTADO FINAL:")
            print(f"   • Tipo: {tipo_final}")
            print(f"   • Confianza: {confianza_final:.1f}%")
            
            self.tdah_type = tipo_final
            self.tdah_confidence = confianza_final
            self.last_evaluation_date = datetime.utcnow()
            
            print(f"   • Estado actualizado ✓")
        else:
            print(f"\n⚠️  No se pudo determinar tipo (confianza insuficiente)")
        
        print(f"{'='*60}\n")
        
        return {
            'tipo': tipo_final,
            'confianza': confianza_final,
            'vision_tests': len(vision_data),
            'audio_tests': len(audio_data),
            'stroop_tests': len(stroop_data),
            'gonogo_tests': len(gonogo_data)
        }
    
    def _algoritmo_consenso(self, vision_data, audio_data, stroop_data, gonogo_data):
        """Algoritmo de consenso con peso temporal"""
        from flask import current_app
        threshold = current_app.config.get('TDAH_MIN_CONFIDENCE', 50)
        
        print(f"\n🧮 APLICANDO ALGORITMO DE CONSENSO (threshold={threshold}%):")
        
        scores = {
            'typical': {'total': 0, 'count': 0, 'confidences': []},
            'inatento': {'total': 0, 'count': 0, 'confidences': []},
            'hiperactivo': {'total': 0, 'count': 0, 'confidences': []},
            'combinado': {'total': 0, 'count': 0, 'confidences': []}
        }
        
        all_data_sets = [
            ('Visión', '📹', vision_data),
            ('Audio', '🎤', audio_data),
            ('Stroop', '🎨', stroop_data),
            ('Go/No-Go', '🎮', gonogo_data),
        ]
        
        for nombre, emoji, dataset in all_data_sets:
            for idx, data in enumerate(dataset):
                tipo = data['tipo']
                confianza = data['confianza']
                peso_temporal = max(0.4, 1.0 - (idx * 0.2))
                score = confianza * peso_temporal
                
                if tipo in scores:
                    scores[tipo]['total'] += score
                    scores[tipo]['count'] += 1
                    scores[tipo]['confidences'].append(confianza)
                
                print(f"   {emoji} {nombre} #{idx+1}: {tipo} ({confianza}%) → score: {score:.1f}")
        
        print(f"\n📈 SCORES FINALES:")
        resultados = {}
        for tipo, data in scores.items():
            if data['count'] > 0:
                promedio = data['total'] / data['count']
                resultados[tipo] = promedio
                print(f"   • {tipo}: {promedio:.1f} (basado en {data['count']} tests)")
            else:
                resultados[tipo] = 0
        
        if not resultados or max(resultados.values()) == 0:
            return None, 0
        
        tipo_ganador = max(resultados, key=resultados.get)
        confianza_final = resultados[tipo_ganador]
        
        if confianza_final < threshold:
            print(f"\n⚠️  Confianza insuficiente ({confianza_final:.1f}% < {threshold}%)")
            return None, confianza_final
        
        return tipo_ganador, confianza_final
    
    def necesita_reevaluacion(self):
        """Determina si el estudiante necesita re-evaluación"""
        from flask import current_app
        reeval_days = current_app.config.get('TDAH_REEVAL_DAYS', 30)
        min_confidence = current_app.config.get('TDAH_MIN_CONFIDENCE', 50) + 10
        
        if not self.tdah_type:
            return True
        if self.tdah_confidence < min_confidence:
            return True
        if self.last_evaluation_date:
            dias = (datetime.utcnow() - self.last_evaluation_date).days
            if dias > reeval_days:
                return True
        return False
    
    def get_tipo_tdah_display(self):
        """Retorna el tipo de TDAH en formato amigable"""
        tipos_display = {
            'typical': 'Típico (Sin TDAH)',
            'inatento': 'TDAH - Inatento',
            'hiperactivo': 'TDAH - Hiperactivo',
            'combinado': 'TDAH - Combinado'
        }
        return tipos_display.get(self.tdah_type, 'No evaluado')
    
    def get_display_name(self):
        """Retorna nombre completo si existe, sino username"""
        return self.full_name or (self.user.username if self.user else 'Sin nombre')
    
    def get_parents(self):
        """Retorna los padres/tutores vinculados con sus datos"""
        from app.models.parent import ParentStudent, Parent
        from app.extensions import db
        
        result = []
        links = ParentStudent.query.filter_by(student_id=self.id).all()
        for link in links:
            parent = db.session.get(Parent, link.parent_id)
            if parent:
                result.append({
                    'parent': parent,
                    'relationship': link.relationship,
                    'phone': parent.phone,
                    'email': parent.user.email if parent.user else None,
                    'name': parent.get_display_name()
                })
        return result
    
    def get_confianza_color(self):
        """Retorna clase de Bootstrap según nivel de confianza"""
        if not self.tdah_confidence:
            return 'secondary'
        if self.tdah_confidence >= 80:
            return 'success'
        elif self.tdah_confidence >= 60:
            return 'info'
        elif self.tdah_confidence >= 40:
            return 'warning'
        else:
            return 'danger'