"""De un término de búsqueda a una expresión regular compilada."""

import re
import unicodedata

from .text import strip_accents

RE_PREFIX = "re:"


class PatternError(Exception):
    """Una expresión regular mal formada."""


def is_regex_term(term: str, as_regex: bool) -> bool:
    """Un término es patrón si se pasó --regex o si empieza por 're:'."""
    return as_regex or term.startswith(RE_PREFIX)


def display_term(term: str) -> str:
    """Quita el prefijo «re:» para que el rótulo sirva tal cual en un índice."""
    return term.removeprefix(RE_PREFIX)


def build_pattern(term: str, *, as_regex: bool = False,
                  substring: bool = False, case_sensitive: bool = False,
                  ignore_accents: bool = False,
                  regex_word: bool = False) -> re.Pattern[str]:
    """Compila el patrón de un término. Lanza PatternError si está mal
    formado."""
    pattern_mode = is_regex_term(term, as_regex)
    term = term.removeprefix(RE_PREFIX)

    if ignore_accents:
        # Al texto de las páginas ya se le quitaron los diacríticos, así que
        # hay que quitárselos también al patrón. Solo se ven afectados los
        # caracteres literales acentuados; secuencias como \w quedan igual.
        term = strip_accents(unicodedata.normalize("NFKC", term))

    if pattern_mode:
        body = term
        # Por omisión las expresiones regulares no se tocan: delimitarlas es
        # tarea de quien las escribe. --regex-word les aplica los mismos
        # límites de palabra que a los términos literales.
        if regex_word and not substring:
            body = rf"(?<!\w)(?:{body})(?!\w)"
    else:
        # una frase puede partirse al final del renglón -> espacios flexibles
        body = r"\s+".join(re.escape(w) for w in term.split())
        if not substring:
            # \b falla junto a caracteres no alfanuméricos; con lookarounds
            # funcionan también los términos con apóstrofo, guion o puntuación.
            body = rf"(?<!\w){body}(?!\w)"

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        return re.compile(body, flags)
    except re.error as exc:
        raise PatternError(
            f"expresión regular mal formada «{term}»: {exc}") from None
