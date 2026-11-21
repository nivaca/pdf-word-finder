import pytest

from pdf_word_finder import (Options, PdfError, extract_pages, read_terms,
                             search)


def pages_of(result, term):
    return [h.label for h in result.hits[term]]


def test_extract_labels(labelled_pdf):
    doc = extract_pages(labelled_pdf)
    assert doc.has_labels
    assert doc.labels == ["i", "ii", "1", "2", "3", "4", "5"]
    assert len(doc.texts) == 7


def test_extract_without_labels(plain_pdf):
    doc = extract_pages(plain_pdf)
    assert not doc.has_labels
    assert doc.labels == [str(i) for i in range(1, 8)]


def test_extract_missing_file(tmp_path):
    with pytest.raises(PdfError, match="no se encontró"):
        extract_pages(str(tmp_path / "nope.pdf"))


def test_extract_not_a_pdf(tmp_path):
    bad = tmp_path / "bad.pdf"
    bad.write_text("this is not a PDF")
    with pytest.raises(PdfError, match="no se pudo abrir"):
        extract_pages(str(bad))


def test_search_reports_printed_pages(labelled_pdf):
    r = search(extract_pages(labelled_pdf), ["amor", "Sharahzad"], Options())
    assert pages_of(r, "amor") == ["i", "1", "2"]
    assert pages_of(r, "Sharahzad") == ["ii", "1"]
    assert r.empty_pages == 1 and r.total_pages == 7


def test_search_dehyphenation(labelled_pdf):
    doc = extract_pages(labelled_pdf)
    assert pages_of(search(doc, ["virtus"], Options()), "virtus") == ["1", "5"]
    off = search(doc, ["virtus"], Options(dehyphenate=False))
    assert pages_of(off, "virtus") == ["5"]


def test_search_counts_and_context(labelled_pdf):
    r = search(extract_pages(labelled_pdf), ["re:virtu(s|tem|tis)"],
               Options(context_width=10))
    last = r.hits["re:virtu(s|tem|tis)"][-1]
    assert (last.logical, last.label, last.count) == (7, "5", 3)
    assert len(last.snippets) == 3
    assert last.snippets[0].startswith("Virtus")
    assert r.total() == 4 and r.pages_with_hits() == 2


def test_search_ignore_accents(labelled_pdf):
    r = search(extract_pages(labelled_pdf), ["ambito"],
               Options(ignore_accents=True))
    assert r.hits["ambito"][0].count == 2


def test_read_terms():
    lines = ["amor\n", "# comentario\n", "  virtus  # latín\n", "\n"]
    assert read_terms(lines) == ["amor", "virtus"]
