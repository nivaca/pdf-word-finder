"""Fixtures: PDF pequeños con texto de verdad, con y sin árbol /PageLabels.

Se generan con pypdf en cada sesión de pruebas, de modo que el repositorio
no necesita guardar archivos PDF.
"""

import pytest
from pypdf import PdfWriter
from pypdf.constants import PageLabelStyle
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

# Siete páginas. Con rótulos: i, ii, y luego 1-5 desde la tercera. La sexta
# está vacía, como una página escaneada sin OCR.
PAGES = [
    "Prefacio sobre el amor y la philología.",
    "Índice general. Sharahzad aparece aquí.",
    "Capítulo uno. El amor de Sharahzad y la vir-\ntus romana. Leña y lengua.",
    "De rerum\nnatura: amor, amoris, amorem. Marcolphus habla.",
    "Página sin nada que buscar.",
    "",
    "Virtus, virtutem, virtutis. ÁMBITO y ambito. Nombre de Dios.",
]


def make_pdf(path, pages=PAGES, labels=True):
    w = PdfWriter()
    font = w._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
        NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
    }))
    for text in pages:
        page = w.add_blank_page(612, 792)
        ops = ["BT", "/F1 12 Tf", "14 TL", "72 720 Td"]
        for line in text.split("\n"):
            line = (line.replace("\\", "\\\\").replace("(", "\\(")
                    .replace(")", "\\)"))
            ops.append(f"({line}) Tj T*")
        ops.append("ET")
        stream = DecodedStreamObject()
        stream.set_data("\n".join(ops).encode("cp1252"))
        page[NameObject("/Contents")] = w._add_object(stream)
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
    if labels:
        w.set_page_label(0, 1, style=PageLabelStyle.LOWERCASE_ROMAN)
        w.set_page_label(2, 6, style=PageLabelStyle.DECIMAL)
    with open(path, "wb") as fh:
        w.write(fh)
    return str(path)


@pytest.fixture(scope="session")
def labelled_pdf(tmp_path_factory):
    return make_pdf(tmp_path_factory.mktemp("pdf") / "rotulado.pdf")


@pytest.fixture(scope="session")
def plain_pdf(tmp_path_factory):
    return make_pdf(tmp_path_factory.mktemp("pdf") / "sin_rotulos.pdf",
                    labels=False)


@pytest.fixture(autouse=True)
def no_pymupdf(monkeypatch):
    """Las pruebas usan siempre pypdf, esté o no instalado PyMuPDF, para
    que el resultado no dependa de la máquina."""
    monkeypatch.setattr("pdf_word_finder.extraction.load_pymupdf",
                        lambda: None)
