from datetime import datetime

from app.extensions import db


class PedagogicalSession(db.Model):
    """Sesión pedagógica física guiada por el maestro con el niño.

    Distinta de Session (actividad AR/cognitiva que el niño completa en el
    dispositivo). Acá el maestro trabaja cara a cara con una hoja impresa.
    """
    __tablename__ = 'pedagogical_sessions'

    id = db.Column(db.Integer, primary_key=True)
    # students.id, no users.id: es la convención del resto del proyecto
    # (Report.student_id y Activity.student_id apuntan a students).
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Recomendación de la IA (Fase 2)
    ai_recommendation = db.Column(db.JSON, nullable=True)
    recommendation_generated_at = db.Column(db.DateTime, nullable=True)

    # Plan generado por la IA
    session_title = db.Column(db.String(255), nullable=True)
    session_area = db.Column(db.String(100), nullable=True)   # atencion, memoria, control_inhibitorio...
    session_level = db.Column(db.Integer, nullable=True)      # 1-5
    teacher_guide = db.Column(db.Text, nullable=True)
    student_worksheet = db.Column(db.Text, nullable=True)
    rubric = db.Column(db.JSON, nullable=True)
    pdf_generated_at = db.Column(db.DateTime, nullable=True)

    # draft, planned, in_progress, completed, evaluated
    status = db.Column(db.String(50), default='draft', index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    scheduled_for = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    student = db.relationship('Student', foreign_keys=[student_id],
                              backref=db.backref('pedagogical_sessions', lazy='dynamic'))
    teacher = db.relationship('User', foreign_keys=[teacher_id],
                              backref=db.backref('pedagogical_sessions_as_teacher', lazy='dynamic'))
    results = db.relationship('SessionResult', backref='session', lazy='dynamic',
                              cascade='all, delete-orphan')

    STATUS_LABELS = {
        'draft': 'Borrador',
        'planned': 'Planificada',
        'in_progress': 'En progreso',
        'completed': 'Completada',
        'evaluated': 'Evaluada',
    }

    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status or '—')

    def __repr__(self):
        return f'<PedagogicalSession {self.id} student={self.student_id} status={self.status}>'


class SessionResult(db.Model):
    """Resultado que el maestro registra después de una sesión pedagógica."""
    __tablename__ = 'session_results'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('pedagogical_sessions.id'),
                           nullable=False, index=True)

    teacher_notes = db.Column(db.Text, nullable=False)
    objective_metrics = db.Column(db.JSON, nullable=True)

    # Análisis de la IA (Fase 2)
    ai_analysis = db.Column(db.Text, nullable=True)
    ai_score = db.Column(db.Float, nullable=True)
    ai_qualitative_grade = db.Column(db.String(50), nullable=True)
    ai_next_recommendation = db.Column(db.Text, nullable=True)
    ai_analyzed_at = db.Column(db.DateTime, nullable=True)

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<SessionResult {self.id} session={self.session_id}>'
