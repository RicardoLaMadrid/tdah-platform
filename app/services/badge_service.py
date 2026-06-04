"""
Servicio de insignias: definición de criterios y lógica de otorgamiento.
Llamar check_and_award_badges(student) desde cualquier ruta tras completar un test.
"""
from datetime import datetime
from app.extensions import db

BADGE_DEFINITIONS = [
    {
        "name": "Primer Test",
        "description": "¡Completaste tu primer test cognitivo!",
        "icon": "🎉",
        "criteria": {"type": "total_tests", "threshold": 1},
    },
    {
        "name": "Racha de 3",
        "description": "3 días seguidos practicando.",
        "icon": "🔥",
        "criteria": {"type": "streak", "threshold": 3},
    },
    {
        "name": "Maestro Stroop",
        "description": "5 tests Stroop con precisión > 80%.",
        "icon": "🎨",
        "criteria": {"type": "stroop_high", "threshold": 5},
    },
    {
        "name": "Explorador AR",
        "description": "Probaste las 4 actividades de realidad aumentada.",
        "icon": "🚀",
        "criteria": {"type": "ar_activities", "threshold": 4},
    },
    {
        "name": "Persistente",
        "description": "10 tests cognitivos completados.",
        "icon": "💎",
        "criteria": {"type": "total_tests", "threshold": 10},
    },
]


def ensure_badges_exist():
    """Crea las insignias predefinidas si no existen."""
    from app.core.models.badge import Badge
    for defn in BADGE_DEFINITIONS:
        if not Badge.query.filter_by(name=defn["name"]).first():
            badge = Badge(**defn)
            db.session.add(badge)
    db.session.commit()


def check_and_award_badges(student) -> list:
    """
    Evalúa todos los criterios para el estudiante y otorga las insignias
    que aún no tiene. Retorna lista de Badge recién otorgados.
    """
    from app.core.models.badge import Badge, StudentBadge
    from app.core.models.report import Report
    from app.core.models.activity import Session, Activity
    from sqlalchemy import cast, Date as SqlDate

    ensure_badges_exist()

    existing_ids = {sb.badge_id for sb in student.badges.all()}
    awarded = []

    total_tests = Report.query.filter(
        Report.student_id == student.id,
        Report.report_type.in_(["vision_test", "audio_test", "stroop_test", "gonogo_test"]),
    ).count()

    # Racha
    streak = _calcular_racha_simple(student.id)

    # Stroop con precisión alta
    stroop_high = _count_stroop_high(student.id)

    # Tipos de AR distintos
    ar_types = _count_ar_types(student.id)

    evaluations = {
        "total_tests": total_tests,
        "streak": streak,
        "stroop_high": stroop_high,
        "ar_activities": ar_types,
    }

    for badge in Badge.query.all():
        if badge.id in existing_ids:
            continue
        crit = badge.criteria or {}
        crit_type = crit.get("type")
        threshold = crit.get("threshold", 1)
        value = evaluations.get(crit_type, 0)
        if value >= threshold:
            sb = StudentBadge(student_id=student.id, badge_id=badge.id)
            db.session.add(sb)
            awarded.append(badge)

    if awarded:
        db.session.commit()

    return awarded


def get_student_badges(student) -> list:
    """Retorna lista de Badge del estudiante."""
    from app.core.models.badge import Badge, StudentBadge
    return (
        db.session.query(Badge)
        .join(StudentBadge, StudentBadge.badge_id == Badge.id)
        .filter(StudentBadge.student_id == student.id)
        .all()
    )


def _calcular_racha_simple(student_id: int) -> int:
    from app.core.models.activity import Session
    from app.core.models.report import Report
    from sqlalchemy import cast, Date as SqlDate
    from datetime import date, timedelta

    today = datetime.utcnow().date()
    streak = 0
    for offset in range(30):
        day = today - timedelta(days=offset)
        has = db.session.query(Session.id).filter(
            Session.student_id == student_id,
            cast(Session.created_at, SqlDate) == day,
        ).first() or db.session.query(Report.id).filter(
            Report.student_id == student_id,
            cast(Report.created_at, SqlDate) == day,
            Report.report_type != "manual_teacher",
        ).first()
        if has:
            streak += 1
        elif streak > 0:
            break
    return streak


def _count_stroop_high(student_id: int) -> int:
    import json
    from app.core.models.report import Report

    reports = Report.query.filter_by(
        student_id=student_id, report_type="stroop_test"
    ).all()
    count = 0
    for r in reports:
        try:
            data = json.loads(r.content or "{}")
            # Usa inhibicion_cognitiva > 80 o confianza > 80 como proxy de "alta precisión"
            if data.get("inhibicion_cognitiva", 0) > 80 or data.get("confianza", 0) > 80:
                count += 1
        except Exception:
            pass
    return count


def _count_ar_types(student_id: int) -> int:
    from app.core.models.activity import Session, Activity

    types = (
        db.session.query(Activity.activity_type)
        .join(Session, Session.activity_id == Activity.id)
        .filter(Session.student_id == student_id)
        .distinct()
        .all()
    )
    ar_types = {t[0] for t in types if t[0] and t[0].startswith("ar_")}
    return len(ar_types)
