import re
from pathlib import Path

from conftest import FEATURES_DIR, tc_scenarios

MATRIX = Path(__file__).parents[2] / "docs" / "test-cases.md"
ROW = re.compile(r"^\| (TC-\d{3}) .*\[([\w.]+):(\d+)\]\(\.\./features/([\w.]+)#L(\d+)\)")


def _matrix_rows() -> dict[str, tuple[str, int, str, int]]:
    rows = {}
    for line in MATRIX.read_text(encoding="utf-8").splitlines():
        match = ROW.match(line)
        if match:
            tc, text_file, text_line, link_file, link_line = match.groups()
            rows[tc] = (text_file, int(text_line), link_file, int(link_line))
    return rows


def test_every_tc_in_the_features_is_in_the_matrix_and_vice_versa() -> None:
    assert set(_matrix_rows()) == set(tc_scenarios())


def test_every_matrix_link_points_to_the_line_of_its_scenario() -> None:
    scenarios = tc_scenarios()

    for tc, (text_file, text_line, link_file, link_line) in _matrix_rows().items():
        expected = scenarios[tc]
        assert (text_file, text_line) == expected, tc
        assert (link_file, link_line) == expected, tc


def test_tc_tags_sit_right_above_a_scenario() -> None:
    for tc, (file_name, line) in tc_scenarios().items():
        scenario = (FEATURES_DIR / file_name).read_text(encoding="utf-8").splitlines()[line - 1]
        assert re.match(r"\s*(Cenário|Esquema do Cenário):", scenario), tc
