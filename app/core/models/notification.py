from app.extensions import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    type = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    related_student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    sent_via_whatsapp = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref='notifications')
    related_student = db.relationship('Student', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.title}>'

    @staticmethod
    def create_notification(user_id, title, message, notification_type='info', student_id=None):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            related_student_id=student_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def notify_tutor_of_student(student_id, title, message, notification_type='info', send_whatsapp=True):
        """
        Crea una notificación para el usuario del estudiante y opcionalmente
        envía WhatsApp al tutor registrado en el campo tutor_phone.
        """
        from app.core.models.student import Student
        from app.extensions import db as _db

        student = _db.session.get(Student, student_id)
        if not student:
            return 0

        notif = Notification.create_notification(
            user_id=student.user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            student_id=student_id
        )

        phone = student.tutor_phone or student.emergency_contact_phone
        whatsapp_ok = student.tutor_whatsapp_enabled if student.tutor_phone else True
        if send_whatsapp and phone and whatsapp_ok:
            try:
                from app.notifications.whatsapp import send_whatsapp_message
                from flask import current_app
                if current_app.config.get('WHATSAPP_ENABLED', False):
                    sent = send_whatsapp_message(
                        to_phone=phone,
                        message=f"*{title}*\n\n{message}\n\n_Plataforma TDAH_"
                    )
                    if sent:
                        notif.sent_via_whatsapp = True
                        _db.session.commit()
            except Exception as e:
                print(f"⚠️  WhatsApp falló para {phone}: {e}")

        return 1

    @staticmethod
    def notify_parents_of_student(student_id, title, message, notification_type='info', send_whatsapp=True):
        """Alias de backward-compatibility — delega a notify_tutor_of_student()."""
        return Notification.notify_tutor_of_student(
            student_id, title, message, notification_type, send_whatsapp
        )
