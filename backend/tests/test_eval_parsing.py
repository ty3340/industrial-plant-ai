from eval.run_eval import extract_verdict


def test_explicit_possible():
    assert extract_verdict("...reasoning...\nVERDICT: POSSIBLE") == "POSSIBLE"


def test_explicit_not_possible():
    assert extract_verdict("...\nVERDICT: NOT POSSIBLE") == "NOT POSSIBLE"


def test_fallback_not_possible_substring():
    assert extract_verdict("This is not possible: tank 2 is too low.") == "NOT POSSIBLE"


def test_unknown_when_no_verdict():
    assert extract_verdict("I'm not certain about that.") == "UNKNOWN"
