"""Apertura del PDF: el texto de cada página y su rótulo impreso."""

import importlib
from types import ModuleType
from typing import NamedTuple


class PdfError(Exception):
    """El PDF no existe, no se puede abrir o está cifrado."""


class Document(NamedTuple):
    """Lo que interesa de un PDF.

    texts[i] y labels[i] corresponden ambos a la página secuencial i+1.
    has_labels dice si los rótulos vienen de un árbol /PageLabels real o
    son la numeración secuencial puesta en su lugar.
    """
    texts: list[str]
    labels: list[str]
    has_labels: bool


def load_pymupdf() -> ModuleType | None:
    """Devuelve el módulo de PyMuPDF, o None si no está instalado.

    Se prueba primero «pymupdf», que es el nombre moderno. El antiguo «fitz»
    sigue funcionando, pero imprime un aviso de obsolescencia en la salida
    ordinaria —que ensuciaría la lista al redirigirla a un archivo— y está
    anunciada su desaparición. Se conserva solo como respaldo para versiones
    antiguas de la biblioteca.

    Se carga con importlib, y no con un `import` corriente, para que
    PyInstaller no lo vea y no lo meta en los ejecutables: añadiría unos
    40 MB, y su licencia (AGPL) es otra.
    """
    for name in ("pymupdf", "fitz"):
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    return None


def extract_pages(path: str) -> Document:
    """Lee el PDF de `path`. Lanza PdfError si no puede."""
    from pypdf import PdfReader

    try:
        reader = PdfReader(path)
    except FileNotFoundError:
        raise PdfError(f"no se encontró el archivo «{path}».") from None
    except Exception as exc:
        raise PdfError(f"no se pudo abrir «{path}»: {exc}") from None

    if reader.is_encrypted:
        try:
            reader.decrypt("")  # la contraseña de usuario vacía es frecuente
        except Exception:
            raise PdfError(f"«{path}» está cifrado y no se puede abrir.") \
                from None

    n = len(reader.pages)

    # --- rótulos ---------------------------------------------------------
    # pypdf inventa "1", "2", ... cuando el archivo no tiene árbol
    # /PageLabels, así que se consulta el catálogo para saber si los
    # rótulos son reales.
    has_labels = "/PageLabels" in reader.trailer["/Root"]
    try:
        labels = [str(x) for x in reader.page_labels]
    except Exception:
        labels = []
    if len(labels) != n:  # árbol defectuoso -> numeración secuencial
        labels = [str(i + 1) for i in range(n)]
        has_labels = False

    # --- texto -----------------------------------------------------------
    texts = None
    mupdf = load_pymupdf()  # extrae bastante mejor, si está instalado
    if mupdf is not None:
        with mupdf.open(path) as doc:
            texts = [p.get_text("text") for p in doc]
        if len(texts) != n:
            texts = None

    if texts is None:
        texts = [(p.extract_text() or "") for p in reader.pages]

    return Document(texts, labels, has_labels)
