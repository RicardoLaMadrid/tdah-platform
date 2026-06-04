from app.extensions import db
from datetime import datetime


class Badge(db.Model):
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(20), default="🏅")
    criteria = db.Column(db.JSON)

    awarded = db.relationship("StudentBadge", backref="badge", lazy="dynamic")

    def __repr__(self):
        return f"<Badge {self.name}>"


class StudentBadge(db.Model):
    __tablename__ = "student_badges"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref=db.backref("badges", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("student_id", "badge_id", name="uq_student_badge"),
    )

    def __repr__(self):
        return f"<StudentBadge student={self.student_id} badge={self.badge_id}>"
