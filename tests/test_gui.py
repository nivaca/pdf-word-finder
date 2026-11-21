"""La parte de la interfaz que no necesita pantalla: la búsqueda en segundo
plano y el informe que muestra."""

import pytest

tk = pytest.importorskip("tkinter")

from pdf_word_finder import Options  # noqa: E402
from pdf_word_finder.gui import SearchError, compose_report, run_search  # noqa: E402


def test_run_search_and_report(labelled_pdf):
    r = run_search(labelled_pdf, ["amor", "zzz"], Options())
    text = compose_report(r, show_logical=False, detailed=False,
                          alphabetical=False)
    notes, report = text.split("\n\n")
    assert report == "amor i, 1, 2"
    assert "sin apariciones: zzz" in notes


def test_run_search_errors(labelled_pdf, tmp_path):
    with pytest.raises(SearchError, match="mal formada"):
        run_search(labelled_pdf, ["re:("], Options())
    with pytest.raises(SearchError):
        run_search(str(tmp_path / "nope.pdf"), ["amor"], Options())
