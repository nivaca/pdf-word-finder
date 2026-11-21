"""Normalización del texto de las páginas y orden alfabético español."""

import re
import unicodedata

# Los guiones que pueden partir una palabra a final de renglón: el de
# teclado, el blando, los de u+2010 a u+2014.
_HYPHENS = "-­‐‑‒–—"
_DEHYPH_RE = re.compile(rf"(\w)[{_HYPHENS}][ \t]*\n[ \t]*(\w)")
_WS_RE = re.compile(r"[ \t\r\f\v ]+")


def strip_accents(s: str) -> str:
    """Elimina los signos diacríticos: 'philología' -> 'philologia'."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if not unicodedata.combining(c))


def normalise(text: str, *, dehyphenate: bool = True,
              ignore_accents: bool = False) -> str:
    """Prepara el texto de una página para la búsqueda.

    Deshace ligaduras y otras formas de compatibilidad (NFKC: ﬁ -> fi),
    vuelve a unir las palabras partidas a final de renglón si se pide, pone
    todo en un solo renglón con espacios simples y, si se pide, quita los
    diacríticos.
    """
    text = unicodedata.normalize("NFKC", text)
    if dehyphenate:
        text = _DEHYPH_RE.sub(r"\1\2", text)
    text = text.replace("\n", " ")
    text = _WS_RE.sub(" ", text)
    if ignore_accents:
        text = strip_accents(text)
    return text


def sort_key(s: str) -> str:
    """Clave de ordenación alfabética española.

    Prescinde de tildes y de mayúsculas —«ámbito» y «Ambito» van donde iría
    «ambito»— pero conserva la eñe como letra propia, después de la ene:
    «leña» va detrás de «lengua», como manda el alfabeto español. La ch y la
    ll se ordenan como c+h y l+l, según la reforma de 1994.
    """
    s = unicodedata.normalize("NFC", s).casefold()
    # Se sustituye la eñe antes de quitar diacríticos, que si no la
    # convertirían en una simple ene. ￿ ordena después de cualquier
    # letra, de modo que la eñe queda al final de las enes.
    s = s.replace("ñ", "n￿")
    return strip_accents(s)


def plural(n: int, singular: str, plural_: str) -> str:
    return singular if n == 1 else plural_
