from pdf_word_finder.text import normalise, plural, sort_key, strip_accents


def test_strip_accents():
    assert strip_accents("philología ÁMBITO") == "philologia AMBITO"


def test_normalise_ligatures_and_spaces():
    assert normalise("ﬁn  de la\tpágina\n") == "fin de la página "


def test_normalise_dehyphenates_line_breaks():
    assert normalise("vir-\ntus") == "virtus"
    assert normalise("vir­ \n tus") == "virtus"
    assert normalise("vir-\ntus", dehyphenate=False) == "vir- tus"


def test_normalise_keeps_ordinary_hyphens():
    assert normalise("greco-latino") == "greco-latino"


def test_normalise_ignore_accents():
    assert normalise("Ámbito", ignore_accents=True) == "Ambito"


def test_sort_key_spanish_order():
    words = ["leña", "lengua", "Ámbito", "ambar", "zorro", "llave", "luz"]
    assert sorted(words, key=sort_key) == [
        "ambar", "Ámbito", "lengua", "leña", "llave", "luz", "zorro"]


def test_plural():
    assert plural(1, "página", "páginas") == "página"
    assert plural(0, "página", "páginas") == "páginas"
    assert plural(2, "página", "páginas") == "páginas"
