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

    # Días por defecto para completar una sesión recién recomendada.
    DIAS_PARA_COMPLETAR = 7

    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status or '—')

    # ── Vencimiento ────────────────────────────────────────────────────
    # La fecha límite es scheduled_for. No se agregó un due_date aparte
    # porque serían dos columnas para el mismo dato y habría que mantener
    # las dos en sincronía.

    @property
    def is_completed(self):
        return self.status in ('completed', 'evaluated')

    @property
    def is_expired(self):
        """Venció y todavía no se completó."""
        if not self.scheduled_for or self.is_completed:
            return False
        return datetime.utcnow() > self.scheduled_for

    @property
    def days_remaining(self):
        """Días enteros que faltan. Negativo si ya venció, None si no tiene fecha.

        Se compara por fecha calendario, no por timestamp: si vence hoy más
        tarde, para el docente "faltan 0 días", no "falta 0.7".
        """
        if not self.scheduled_for:
            return None
        return (self.scheduled_for.date() - datetime.utcnow().date()).days

    def due_state(self):
        """(clave, etiqueta, color) del vencimiento, para pintar la cuenta regresiva."""
        if self.is_completed:
            return ('completada', 'Completada', 'verde')

        dias = self.days_remaining
        if dias is None:
            return ('sin_fecha', 'Sin fecha límite', 'gris')

        if dias < 0:
            falta = abs(dias)
            etiqueta = 'Venció ayer' if falta == 1 else f'Venció hace {falta} días'
            return ('vencida', etiqueta, 'gris')

        if dias == 0:
            return ('hoy', 'Vence HOY', 'rojo')

        if dias <= 3:
            return ('pronto', f'Vence en {dias} día' + ('s' if dias != 1 else ''), 'naranja')

        return ('holgado', f'Tenés tiempo · {dias} días', 'verde')

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
