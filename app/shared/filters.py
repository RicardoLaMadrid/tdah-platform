"""Filtros Jinja compartidos por todos los blueprints."""

import re

from markupsafe import Markup, escape

# Un paso arranca con "1." o "1)" al principio del texto o después de un
# espacio/salto de línea. El lookbehind evita partir números que están
# dentro de una frase (ej: "durante 3.5 segundos").
_STEP_SPLIT = re.compile(r'(?:(?<=^)|(?<=\s))(?=\d{1,2}[.)]\s)')
_STEP_PREFIX = re.compile(r'^\d{1,2}[.)]\s*')


def split_steps(text):
    """Separa un texto con pasos numerados en la lista de pasos, sin el prefijo.

    Devuelve (pasos, es_lista). Si no detecta al menos 2 pasos numerados,
    es_lista es False y `pasos` son las líneas del texto tal cual.

    La usan format_instructions (HTML) y el generador de PDF, para que la
    numeración salga igual en pantalla y en papel.
    """
    if not text:
        return [], False

    text = str(text).strip()
    parts = [p.strip() for p in _STEP_SPLIT.split(text) if p.strip()]

    if len(parts) < 2:
        return [ln.strip() for ln in text.splitlines() if ln.strip()], False

    pasos = []
    for part in parts:
        limpio = _STEP_PREFIX.sub('', part).strip()
        if limpio:
            pasos.append(limpio)
    return pasos, True


def format_instructions(text):
    """Convierte instrucciones en texto plano a HTML legible.

    "1. Sentate derecho. 2. Mirá la pantalla." -> <ol><li>...</li></ol>

    Si no detecta pasos numerados, devuelve un párrafo por línea. El texto
    lo escribe el docente en un textarea, así que se escapa siempre: el
    resultado es Markup y NO necesita pasar por |safe en el template.
    """
    if not text:
        return Markup('')

    pasos, es_lista = split_steps(text)

    if not es_lista:
        return Markup(''.join(
            '<p class="leading-relaxed mb-2">{}</p>'.format(escape(ln))
            for ln in pasos
        ))

    return Markup('<ol>{}</ol>'.format(
        ''.join('<li>{}</li>'.format(escape(p)) for p in pasos)
    ))


def register_filters(app):
    app.jinja_env.filters['format_instructions'] = format_instructions
