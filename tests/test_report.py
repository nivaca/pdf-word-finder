import csv

from pdf_word_finder import (Options, build_report, extract_pages, search,
                             write_csv, write_txt)
from pdf_word_finder.report import fmt_page


def result_for(pdf, terms, **kw):
    return search(extract_pages(pdf), terms, Options(**kw))


def test_fmt_page():
    assert fmt_page(3, "1", False) == "1"
    assert fmt_page(3, "1", True) == "1 [sec. 3]"
    assert fmt_page(3, "3", True) == "3"


def test_list_report(labelled_pdf):
    r = result_for(labelled_pdf, ["amor", "Nombre de Dios", "zzz"])
    report, notes = build_report(r)
    assert report == "amor i, 1, 2\nNombre de Dios 5"
    assert "sin apariciones: zzz" in notes
    assert "no arrojaron texto" in notes
    assert "/PageLabels" not in notes


def test_list_report_show_logical(labelled_pdf):
    report, _ = build_report(result_for(labelled_pdf, ["amor"]),
                             show_logical=True)
    assert report == "amor i [sec. 1], 1 [sec. 3], 2 [sec. 4]"


def test_list_report_alphabetical(labelled_pdf):
    r = result_for(labelled_pdf, ["leña", "lengua", "amor"])
    report, _ = build_report(r, alphabetical=True)
    assert [l.split()[0] for l in report.splitlines()] == [
        "amor", "lengua", "leña"]


def test_report_notes_missing_labels(plain_pdf):
    _, notes = build_report(result_for(plain_pdf, ["amor"]))
    assert "no tiene árbol /PageLabels" in notes


def test_detailed_report(labelled_pdf):
    r = result_for(labelled_pdf, ["virtus", "zzz"], context_width=5)
    report, notes = build_report(r, detailed=True)
    lines = report.splitlines()
    assert lines[0] == "«virtus»: 2 apariciones en 2 páginas"
    assert lines[1] == "    1"
    assert "«zzz»: sin apariciones" in report
    assert "sin apariciones" not in notes


def test_write_txt_and_csv(labelled_pdf, tmp_path):
    r = result_for(labelled_pdf, ["re:virtu(s|tem|tis)", "amor"])
    txt = tmp_path / "i.txt"
    assert write_txt(str(txt), r) == 2
    assert txt.read_text(encoding="utf-8") == (
        "amor i, 1, 2\nvirtu(s|tem|tis) 1, 5\n")
    out = tmp_path / "i.csv"
    write_csv(str(out), r)
    rows = list(csv.reader(out.open(encoding="utf-8")))
    assert rows[0][0] == "termino"
    assert rows[1] == ["amor", "1", "i", "1", ""]
    assert rows[-1] == ["virtu(s|tem|tis)", "7", "5", "3", ""]
