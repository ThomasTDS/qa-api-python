import re
from pathlib import Path

import pytest

# Alguns documentos existem em português (o principal) e em inglês. A
# tradução em si não dá para conferir automaticamente, mas a estrutura dá: se
# alguém atualizar só uma das versões (uma seção nova, um comando que mudou,
# um link novo), estes testes falham.
ROOT = Path(__file__).parents[2]
PAIRS = [
    (ROOT / "README.md", ROOT / "README.en.md"),
    (ROOT / "docs" / "test-strategy.md", ROOT / "docs" / "test-strategy.en.md"),
]
PAIR_IDS = [pt.name for pt, _ in PAIRS]

FENCE = "```"
LINK = re.compile(r"\]\(([^)\s]+)\)")


def _blocks_and_prose(path: Path) -> tuple[list[list[str]], list[str]]:
    blocks: list[list[str]] = []
    prose: list[str] = []
    current: list[str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(FENCE):
            if current is None:
                current = []
            else:
                blocks.append(current)
                current = None
        elif current is not None:
            current.append(line)
        else:
            prose.append(line)
    return blocks, prose


def _heading_levels(path: Path) -> list[int]:
    _, prose = _blocks_and_prose(path)
    return [len(line) - len(line.lstrip("#")) for line in prose if line.startswith("#")]


# Comentários (# ...) são traduzidos, então ficam de fora da comparação. O
# resto de cada linha (comandos, nomes de arquivo) precisa ser idêntico.
def _code_without_comments(path: Path) -> list[list[str]]:
    blocks, _ = _blocks_and_prose(path)
    result = []
    for block in blocks:
        lines = [line.split("#", 1)[0].rstrip() if not line.lstrip().startswith("#") else "" for line in block]
        result.append([line for line in lines if line])
    return result


# Os links de troca de idioma apontam um para o outro, então ficam de fora. A
# versão em inglês aponta para as traduções em inglês de outros documentos
# (x.en.md) onde a versão em português aponta para x.md: os dois contam como
# o mesmo destino.
def _links(path: Path, pair: tuple[Path, Path]) -> list[str]:
    _, prose = _blocks_and_prose(path)
    language_links = {pair[0].name, pair[1].name}
    links = (link.replace(".en.md", ".md") for link in LINK.findall("\n".join(prose)))
    return sorted(link for link in links if link not in language_links)


@pytest.mark.parametrize(("pt", "en"), PAIRS, ids=PAIR_IDS)
def test_both_versions_link_to_each_other(pt: Path, en: Path) -> None:
    assert f"]({en.name})" in pt.read_text(encoding="utf-8")
    assert f"]({pt.name})" in en.read_text(encoding="utf-8")


@pytest.mark.parametrize(("pt", "en"), PAIRS, ids=PAIR_IDS)
def test_both_versions_have_the_same_sections(pt: Path, en: Path) -> None:
    assert _heading_levels(pt) == _heading_levels(en)


@pytest.mark.parametrize(("pt", "en"), PAIRS, ids=PAIR_IDS)
def test_both_versions_have_the_same_commands(pt: Path, en: Path) -> None:
    assert _code_without_comments(pt) == _code_without_comments(en)


@pytest.mark.parametrize(("pt", "en"), PAIRS, ids=PAIR_IDS)
def test_both_versions_have_the_same_links(pt: Path, en: Path) -> None:
    assert _links(pt, (pt, en)) == _links(en, (pt, en))
