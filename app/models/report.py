from app import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)
    
    
    report_type = db.Column(db.String(50), index=True)
    
    content = db.Column(db.Text)  
    recommendations = db.Column(db.Text)
    parent_comments = db.Column(db.Text)  
    sent_to_parents = db.Column(db.Boolean, default=False)
    parent_email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
   
    tipo_tdah = db.Column(db.String(50), default='sin_determinar')
    confianza = db.Column(db.Float, default=0)
    result_data = db.Column(db.Text)  # JSON alternativo, mantener por compat
    
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='reports_created')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'session_id': self.session_id,
            'report_type': self.report_type,
            'content': self.content,
            'recommendations': self.recommendations,
            'sent_to_parents': self.sent_to_parents,
            'tipo_tdah': self.tipo_tdah,
            'confianza': self.confianza,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Report {self.id} for Student {self.student_id}>'