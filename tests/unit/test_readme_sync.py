import re
from pathlib import Path

# O README existe em português (README.md, o principal) e em inglês
# (README.en.md). A tradução em si não dá para conferir automaticamente, mas
# a estrutura dá: se alguém atualizar só um dos dois (uma seção nova, um
# comando que mudou, um link novo), estes testes falham.
ROOT = Path(__file__).parents[2]
README_PT = ROOT / "README.md"
README_EN = ROOT / "README.en.md"

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


# Os links de troca de idioma apontam um para o outro, então ficam de fora.
def _links(path: Path) -> list[str]:
    _, prose = _blocks_and_prose(path)
    links = LINK.findall("\n".join(prose))
    return sorted(link for link in links if link not in ("README.md", "README.en.md"))


def test_both_readmes_link_to_each_other() -> None:
    assert "](README.en.md)" in README_PT.read_text(encoding="utf-8")
    assert "](README.md)" in README_EN.read_text(encoding="utf-8")


def test_both_readmes_have_the_same_sections() -> None:
    assert _heading_levels(README_PT) == _heading_levels(README_EN)


def test_both_readmes_have_the_same_commands() -> None:
    assert _code_without_comments(README_PT) == _code_without_comments(README_EN)


def test_both_readmes_have_the_same_links() -> None:
    assert _links(README_PT) == _links(README_EN)
