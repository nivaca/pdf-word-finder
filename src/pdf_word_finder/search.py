"""La búsqueda: cada término en cada página.

La usan por igual el programa de línea de órdenes y la interfaz gráfica, de
modo que los dos encuentran siempre lo mismo.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import NamedTuple

from .extraction import Document
from .patterns import build_pattern
from .text import normalise


@dataclass(frozen=True)
class Options:
    """Las opciones de búsqueda. context_width=None: sin fragmentos de
    contexto; un número: tantos caracteres a cada lado."""
    regex: bool = False
    regex_word: bool = False
    substring: bool = False
    case_sensitive: bool = False
    ignore_accents: bool = False
    dehyphenate: bool = True
    context_width: int | None = None


class Hit(NamedTuple):
    """Las apariciones de un término en una página."""
    logical: int            # página secuencial, desde 1
    label: str              # página rotulada (el número impreso)
    count: int              # número de apariciones en la página
    snippets: list[str]     # fragmentos de contexto, si se pidieron


@dataclass
class Result:
    terms: list[str]
    hits: dict[str, list[Hit]]
    has_labels: bool
    total_pages: int
    empty_pages: int = 0

    def total(self) -> int:
        """Total de apariciones de todos los términos."""
        return sum(h.count for hits in self.hits.values() for h in hits)

    def pages_with_hits(self) -> int:
        return len({h.logical for hits in self.hits.values() for h in hits})


def read_terms(lines: Iterable[str]) -> list[str]:
    """Los términos de una lista, uno por renglón. «#» inicia un
    comentario y los renglones vacíos se saltan."""
    terms = []
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if line:
            terms.append(line)
    return terms


def _snippet(page: str, start: int, end: int, width: int) -> str:
    a, b = max(0, start - width), min(len(page), end + width)
    return (("…" if a else "") + page[a:b].strip()
            + ("…" if b < len(page) else ""))


def search(doc: Document, terms: list[str], opts: Options) -> Result:
    """Busca los términos en el documento. Lanza PatternError si una
    expresión regular está mal formada."""
    pages = [normalise(t, dehyphenate=opts.dehyphenate,
                       ignore_accents=opts.ignore_accents)
             for t in doc.texts]

    patterns = {t: build_pattern(t, as_regex=opts.regex,
                                 substring=opts.substring,
                                 case_sensitive=opts.case_sensitive,
                                 ignore_accents=opts.ignore_accents,
                                 regex_word=opts.regex_word)
                for t in terms}

    hits: dict[str, list[Hit]] = {t: [] for t in terms}
    for idx, page in enumerate(pages):
        for term, pat in patterns.items():
            matches = list(pat.finditer(page))
            if not matches:
                continue
            snippets = []
            if opts.context_width is not None:
                snippets = [_snippet(page, m.start(), m.end(),
                                     opts.context_width) for m in matches]
            hits[term].append(Hit(idx + 1, doc.labels[idx], len(matches),
                                  snippets))

    return Result(terms=list(terms), hits=hits, has_labels=doc.has_labels,
                  total_pages=len(pages),
                  empty_pages=sum(1 for p in pages if not p.strip()))
