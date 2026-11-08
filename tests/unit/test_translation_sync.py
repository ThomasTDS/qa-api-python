import re
from pathlib import Path

import pytest

# Alguns documentos existem em português (o principal) e em outras línguas. A
# tradução em si não dá para conferir automaticamente, mas a estrutura dá: se
# alguém atualizar só uma das versões (uma seção nova, um comando que mudou,
# um link novo), estes testes falham.
ROOT = Path(__file__).parents[2]
DOCUMENTS = [
    [ROOT / "README.md", ROOT / "README.en.md", ROOT / "README.es.md"],
    [ROOT / "docs" / "test-strategy.md", ROOT / "docs" / "test-strategy.en.md"],
]
PAIRS = [(versions[0], translation, versions) for versions in DOCUMENTS for translation in versions[1:]]
PAIR_IDS = [translation.name for _, translation, _ in PAIRS]

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


# Os links de troca de idioma apontam de uma versão para as outras, então
# ficam de fora. Uma tradução pode apontar para a tradução de outro documento
# (x.en.md) onde a versão em português aponta para x.md: os dois contam como
# o mesmo destino.
TRANSLATION_SUFFIX = re.compile(r"\.(en|es)\.md$")


def _links(path: Path, versions: list[Path]) -> list[str]:
    _, prose = _blocks_and_prose(path)
    language_links = {version.name for version in versions}
    links = (TRANSLATION_SUFFIX.sub(".md", link) for link in LINK.findall("\n".join(prose)))
    return sorted(link for link in links if link not in language_links)


@pytest.mark.parametrize(("pt", "translation", "versions"), PAIRS, ids=PAIR_IDS)
def test_every_version_links_to_the_others(pt: Path, translation: Path, versions: list[Path]) -> None:
    text = translation.read_text(encoding="utf-8")
    for other in versions:
        if other != translation:
            assert f"]({other.name})" in text
    assert f"]({translation.name})" in pt.read_text(encoding="utf-8")


@pytest.mark.parametrize(("pt", "translation", "versions"), PAIRS, ids=PAIR_IDS)
def test_both_versions_have_the_same_sections(pt: Path, translation: Path, versions: list[Path]) -> None:
    assert _heading_levels(pt) == _heading_levels(translation)


@pytest.mark.parametrize(("pt", "translation", "versions"), PAIRS, ids=PAIR_IDS)
def test_both_versions_have_the_same_commands(pt: Path, translation: Path, versions: list[Path]) -> None:
    assert _code_without_comments(pt) == _code_without_comments(translation)


@pytest.mark.parametrize(("pt", "translation", "versions"), PAIRS, ids=PAIR_IDS)
def test_both_versions_have_the_same_links(pt: Path, translation: Path, versions: list[Path]) -> None:
    assert _links(pt, versions) == _links(translation, versions)
