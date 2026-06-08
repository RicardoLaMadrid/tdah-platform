from app.extensions import db
from datetime import datetime

class Parent(db.Model):
    __tablename__ = 'parents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(200))  # ⭐ NUEVO
    phone = db.Column(db.String(20))
    whatsapp_enabled = db.Column(db.Boolean, default=True)
    receive_notifications = db.Column(db.Boolean, default=True)  # ⭐ NUEVO
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('parent_profile', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Parent {self.full_name or self.user.username}>'
    
    def get_display_name(self):
        """Retorna nombre completo si existe, sino username"""
        return self.full_name or self.user.username
    
    def get_children(self):
        from app.models.student import Student
        links = ParentStudent.query.filter_by(parent_id=self.id).all()
        children = []
        for link in links:
            student = db.session.get(Student, link.student_id)
            if student:
                children.append({
                    'student': student,
                    'relationship': link.relationship,
                    'link_id': link.id
                })
        return children
    
    def get_notifications_count(self):
        from app.models.notification import Notification
        return Notification.query.filter_by(
            user_id=self.user_id,
            is_read=False
        ).count()


class ParentStudent(db.Model):
    __tablename__ = 'parent_student'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    relationship = db.Column(db.String(50), default='padre/madre')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('parent_id', 'student_id', name='uq_parent_student'),
    )
    
    parent = db.relationship('Parent', backref='student_links')
    student = db.relationship('Student', backref='parent_links')
    
    def __repr__(self):
        return f'<ParentStudent parent={self.parent_id} student={self.student_id}>'


# Notification fue movido a app/models/notification.py