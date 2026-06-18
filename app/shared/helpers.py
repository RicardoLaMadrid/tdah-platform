"""
app/shared/helpers.py — Funciones reutilizables de filtrado para queries SQLAlchemy.
"""
from datetime import datetime, timedelta
from sqlalchemy import or_


def filter_users_query(q=None, role=None, grade=None, section=None,
                       tdah_type=None, teacher_id=None):
    """
    Devuelve una query de User aplicando los filtros dados.
    Los filtros de Student (grade, section, tdah_type, teacher_id) sólo
    tienen efecto cuando role='student' o cuando no se especifica rol.
    """
    from app.core.models.user import User
    from app.core.models.student import Student

    query = User.query

    if role and role != 'all':
        query = query.filter(User.role == role)

    # Filtros que requieren join con Student
    student_filters_active = any([grade, section, tdah_type is not None and tdah_type != '',
                                   teacher_id])
    searching_with_name = q and (role == 'student' or not role or role == 'all')

    if student_filters_active or searching_with_name:
        if student_filters_active:
            query = query.join(Student, Student.user_id == User.id)
        else:
            query = query.outerjoin(Student, Student.user_id == User.id)

        if grade:
            query = query.filter(Student.grade == grade)
        if section:
            query = query.filter(Student.section == section)
        if tdah_type:
            if tdah_type == 'sin_evaluar':
                query = query.filter(Student.tdah_type.is_(None))
            else:
                query = query.filter(Student.tdah_type == tdah_type)
        if teacher_id:
            query = query.filter(Student.teacher_id == int(teacher_id))

        if q:
            t = f'%{q}%'
            query = query.filter(
                or_(User.username.ilike(t),
                    User.email.ilike(t),
                    Student.full_name.ilike(t))
            )
    elif q:
        t = f'%{q}%'
        query = query.filter(
            or_(User.username.ilike(t), User.email.ilike(t))
        )

    return query.order_by(User.created_at.desc())


def build_observations(ai_draft):
    """Combina resumen_ejecutivo + fortalezas + areas_mejora en prosa para textarea."""
    if not ai_draft:
        return ''
    parts = []
    if ai_draft.get('resumen_ejecutivo'):
        parts.append(ai_draft['resumen_ejecutivo'])
    if ai_draft.get('fortalezas'):
        parts.append('\n\nFortalezas observadas:')
        for f in ai_draft['fortalezas']:
            parts.append('• ' + f)
    if ai_draft.get('areas_mejora'):
        parts.append('\n\nÁreas de mejora:')
        for a in ai_draft['areas_mejora']:
            parts.append('• ' + a)
    return '\n'.join(parts)


def build_recommendations(ai_draft):
    """Convierte la lista de recomendaciones de la IA en texto con bullets."""
    if not ai_draft or not ai_draft.get('recomendaciones'):
        return ''
    parts = []
    for r in ai_draft['recomendaciones']:
        titulo = r.get('titulo', '')
        desc = r.get('descripcion', '')
        prioridad = (r.get('prioridad') or '').upper()
        parts.append(f'• [{prioridad}] {titulo}: {desc}')
    return '\n'.join(parts)


def filter_students_query(teacher_id_filter, q=None, tdah_type=None,
                          grade=None, activity_status=None, sort=None):
    """
    Devuelve una query de Student para un profesor dado, con filtros opcionales.
    """
    from app.core.models.student import Student
    from app.core.models.user import User
    from app.core.models.report import Report
    from app.extensions import db

    query = (
        Student.query
        .filter_by(teacher_id=teacher_id_filter)
        .join(User, User.id == Student.user_id)
    )

    if q:
        t = f'%{q}%'
        query = query.filter(
            or_(Student.full_name.ilike(t), User.username.ilike(t))
        )

    if tdah_type:
        if tdah_type == 'sin_evaluar':
            query = query.filter(Student.tdah_type.is_(None))
        else:
            query = query.filter(Student.tdah_type == tdah_type)

    if grade:
        query = query.filter(Student.grade == grade)

    if activity_status == 'recent':
        cutoff = datetime.utcnow() - timedelta(days=7)
        recent_ids = [
            r[0] for r in db.session.query(Report.student_id)
            .filter(Report.created_at >= cutoff,
                    Report.report_type != 'manual_teacher')
            .distinct()
        ]
        query = query.filter(Student.id.in_(recent_ids))
    elif activity_status == 'inactive':
        cutoff = datetime.utcnow() - timedelta(days=14)
        active_ids = [
            r[0] for r in db.session.query(Report.student_id)
            .filter(Report.created_at >= cutoff,
                    Report.report_type != 'manual_teacher')
            .distinct()
        ]
        query = query.filter(Student.id.notin_(active_ids))

    # MariaDB no soporta NULLS LAST: usar CASE para poner NULLs al final
    from sqlalchemy import case as sa_case
    if sort == 'name':
        query = query.order_by(
            sa_case((Student.full_name.is_(None), 1), else_=0),
            Student.full_name.asc()
        )
    elif sort == 'tdah':
        query = query.order_by(
            sa_case((Student.tdah_type.is_(None), 1), else_=0),
            Student.tdah_type.asc()
        )
    else:
        query = query.order_by(
            sa_case((Student.last_evaluation_date.is_(None), 1), else_=0),
            Student.last_evaluation_date.desc()
        )

    return query


def get_student_filter_options(teacher_id=None):
    """
    Devuelve los valores únicos de grade, section y teachers
    para poblar los dropdowns de filtros.
    """
    from app.core.models.student import Student
    from app.core.models.user import User
    from app.extensions import db

    base = Student.query
    if teacher_id:
        base = base.filter_by(teacher_id=teacher_id)

    grades = sorted([
        r[0] for r in db.session.query(Student.grade)
        .filter(Student.grade.isnot(None))
        .distinct()
        .all()
    ])
    sections = sorted([
        r[0] for r in db.session.query(Student.section)
        .filter(Student.section.isnot(None))
        .distinct()
        .all()
    ])
    teachers = (
        User.query
        .filter_by(role='teacher')
        .order_by(User.username)
        .all()
    )
    return grades, sections, teachers
