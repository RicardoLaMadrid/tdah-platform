from app.extensions import db
from datetime import datetime, timedelta


class ActiveTestSession(db.Model):
    """
    Almacena el estado acumulado de un test cognitivo mientras se realiza.
    Reemplaza los dicts en memoria (test_sessions = {}) que se perdían en
    cada hot-reload del servidor de desarrollo.
    """
    __tablename__ = "active_test_sessions"

    session_id = db.Column(db.String(120), primary_key=True)
    test_type  = db.Column(db.String(20),  nullable=False, index=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    data       = db.Column(db.JSON,    nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User", backref=db.backref("active_tests", lazy="dynamic"))

    def __repr__(self):
        return f"<ActiveTestSession {self.session_id} ({self.test_type})>"

    @staticmethod
    def cleanup_stale(test_type: str, hours: int = 2) -> int:
        """Elimina sesiones abandonadas de más de `hours` horas. Retorna filas eliminadas."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        deleted = ActiveTestSession.query.filter(
            ActiveTestSession.test_type == test_type,
            ActiveTestSession.created_at < cutoff,
        ).delete()
        db.session.commit()
        return deleted
