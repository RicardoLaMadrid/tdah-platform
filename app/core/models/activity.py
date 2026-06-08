from app.extensions import db
from datetime import datetime

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ar_content = db.Column(db.JSON)
    difficulty_level = db.Column(db.Integer, default=1)
    activity_type = db.Column(db.String(50))
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    sessions = db.relationship('Session', backref='activity', cascade='all, delete-orphan', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[teacher_id], backref='activities_created')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'title': self.title,
            'description': self.description,
            'ar_content': self.ar_content,
            'difficulty_level': self.difficulty_level,
            'activity_type': self.activity_type,
            'instructions': self.instructions,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Activity {self.title}>'


class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    video_path = db.Column(db.String(255))
    audio_path = db.Column(db.String(255))
    heatmap_path = db.Column(db.String(255))
    transcription = db.Column(db.Text)
    analysis_result = db.Column(db.JSON)
    attention_score = db.Column(db.Float)
    completion_time = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    reports = db.relationship('Report', backref='session', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'activity_id': self.activity_id,
            'video_path': self.video_path,
            'audio_path': self.audio_path,
            'heatmap_path': self.heatmap_path,
            'transcription': self.transcription,
            'analysis_result': self.analysis_result,
            'attention_score': self.attention_score,
            'completion_time': self.completion_time,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Session {self.id} - Student {self.student_id}>'