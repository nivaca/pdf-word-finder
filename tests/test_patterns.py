import pytest

from pdf_word_finder.patterns import (PatternError, build_pattern,
                                      display_term, is_regex_term)


def found(term, text, **kw):
    return [m.group(0) for m in build_pattern(term, **kw).finditer(text)]


def test_whole_words_by_default():
    assert found("amor", "amor, amoris, Amor") == ["amor", "Amor"]


def test_substring():
    assert found("amor", "amor, amoris", substring=True) == ["amor", "amor"]


def test_case_sensitive():
    assert found("Amor", "amor Amor", case_sensitive=True) == ["Amor"]


def test_phrase_with_flexible_spaces():
    assert found("de rerum natura", "de  rerum\nnatura") == ["de  rerum\nnatura"]


def test_terms_with_punctuation():
    assert found("O'Brien", "Mr O'Brien said") == ["O'Brien"]


def test_regex_prefix_and_flag():
    assert found("re:virtu(s|tem)", "virtus virtutem") == ["virtus", "virtutem"]
    assert found("am(oris|or)", "amor amoris", as_regex=True) == [
        "amor", "amoris"]


def test_regex_is_not_bounded_unless_asked():
    assert found("re:amor", "clamor") == ["amor"]
    assert found("re:amor", "clamor", regex_word=True) == []


def test_ignore_accents_strips_the_term_too():
    assert found("philología", "philologia", ignore_accents=True) == [
        "philologia"]


def test_bad_regex():
    with pytest.raises(PatternError, match="mal formada"):
        build_pattern("re:(")


def test_display_term_and_is_regex():
    assert display_term("re:amor|virtus") == "amor|virtus"
    assert display_term("amor") == "amor"
    assert is_regex_term("re:x", False) and is_regex_term("x", True)
    assert not is_regex_term("x", False)
