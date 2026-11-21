import pytest

from pdf_word_finder import __version__
from pdf_word_finder.cli import main


def run(capsys, *args):
    main(list(args))
    return capsys.readouterr()


def test_basic(capsys, labelled_pdf):
    out = run(capsys, labelled_pdf, "amor", "Sharahzad", "nada")
    assert out.out == "amor i, 1, 2\nSharahzad ii, 1\nnada 3\n"
    assert "no arrojaron texto" in out.err


def test_words_file_sort_and_exports(capsys, labelled_pdf, tmp_path):
    terms = tmp_path / "t.txt"
    terms.write_text("amor\n# nada\nlengua\nleña\n", encoding="utf-8")
    txt, csv_ = tmp_path / "o.txt", tmp_path / "o.csv"
    out = run(capsys, labelled_pdf, "--words-file", str(terms), "--sort",
              "--txt", str(txt), "--csv", str(csv_))
    assert out.out == "amor i, 1, 2\nlengua 1\nleña 1\n"
    assert txt.read_text(encoding="utf-8") == out.out
    assert "lista de 3 entradas" in out.err and "CSV escrito" in out.err


def test_context_implies_detailed(capsys, labelled_pdf):
    out = run(capsys, labelled_pdf, "amor", "--context", "--context-width",
              "5")
    assert out.out.startswith("«amor»: 3 apariciones en 3 páginas\n    i\n")


@pytest.mark.parametrize("args, message", [
    (["nope.pdf", "amor"], "no se encontró el archivo"),
    (["{pdf}", "re:("], "mal formada"),
    (["{pdf}", "--words-file", "/no/such/file"], "no se pudo leer"),
])
def test_errors(capsys, labelled_pdf, args, message):
    args = [a.format(pdf=labelled_pdf) for a in args]
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert message in str(exc.value.code)


def test_no_terms(capsys, labelled_pdf):
    with pytest.raises(SystemExit) as exc:
        main([labelled_pdf])
    assert exc.value.code == 2
    assert "no se indicó ningún término" in capsys.readouterr().err


def test_version_and_spanish_help(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert capsys.readouterr().out.startswith(f"pdf-word-finder {__version__}")
    with pytest.raises(SystemExit):
        main(["--help"])
    help_text = capsys.readouterr().out
    assert help_text.startswith("uso: pdf-word-finder")
    assert "opciones:" in help_text
