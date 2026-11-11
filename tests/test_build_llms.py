"""Tests du générateur de llms.txt."""
from __future__ import annotations

from pathlib import Path

from scripts.build_llms import main, render_llms

CONFIG = """[project]
site_url = "https://example.be/"
nav = [
  { "Rubrique" = [
    "rubrique/README.md",
    { "Page du menu" = "rubrique/page.md" },
    { "Brouillon" = "rubrique/brouillon.md" },
  ] },
  { "Actualités" = [
    "actualites/README.md",
  ] },
]
"""

PAGES = {
    "README.md": "# Accueil\n",
    "faq/README.md": "---\ndescription: Les questions\n---\n# FAQ\n",
    "delais.md": "---\ndescription: Les délais\n---\n# Délais clés\n",
    "rubrique/README.md": "---\ndescription: Entrée\n  de rubrique\n---\n# Titre de la rubrique\n",
    "rubrique/page.md": "---\ndescription: Une page\n---\n# Titre long [H1]\n",
    "rubrique/brouillon.md": "---\ndescription: Pas prêt\ndraft: true\n---\n# Brouillon\n",
    "actualites/README.md": "---\ndescription: Les notes\n---\n# Actualités\n",
    "actualites/2026-10-01-passee.md": (
        "---\ntitle: Note passée\ndate: '2026-10-01'\ndescription: Publiée\n---\n# Note passée\n"
    ),
    "actualites/2026-12-01-future.md": (
        "---\ntitle: Note future\ndate: '2026-12-01'\ndescription: Programmée\n---\n# Note future\n"
    ),
}


def _site(tmp_path: Path) -> Path:
    (tmp_path / "zensical.toml").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "overrides").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "llms-intro.md").write_text(
        "# Site\n\n> Résumé du site.\n", encoding="utf-8"
    )
    for rel, content in PAGES.items():
        path = tmp_path / "docs" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp_path


def _body(text: str) -> str:
    """Le fichier est publié tel quel : il doit commencer par le H1."""
    assert text.startswith("# ")
    return text


def test_starts_with_h1_and_summary_quote(tmp_path: Path) -> None:
    body = _body(render_llms(_site(tmp_path), today="2026-11-11"))
    assert body.startswith("# Site\n\n> Résumé du site.\n")


def test_nav_sections_in_order_with_menu_labels_and_descriptions(tmp_path: Path) -> None:
    body = _body(render_llms(_site(tmp_path), today="2026-11-11"))
    assert body.index("## Rubrique") < body.index("## Actualités") < body.index(
        "## Questions fréquentes"
    ) < body.index("## Pages utiles") < body.index("## Optional")
    # Page d'entrée : titre H1 ; description repliée sur une ligne.
    assert "- [Titre de la rubrique](https://example.be/rubrique/): Entrée de rubrique" in body
    # Page du menu : libellé du menu, pas le H1.
    assert "- [Page du menu](https://example.be/rubrique/page/): Une page" in body
    assert "- [Délais clés](https://example.be/delais/): Les délais" in body


def test_excludes_drafts_and_scheduled_notes(tmp_path: Path) -> None:
    body = _body(render_llms(_site(tmp_path), today="2026-11-11"))
    assert "brouillon" not in body
    assert "- [Note passée](https://example.be/actualites/2026-10-01-passee/): Publiée" in body
    assert "future" not in body


def test_check_fails_when_out_of_date_then_passes(tmp_path: Path) -> None:
    site = _site(tmp_path)
    assert main(["--check", "--today", "2026-11-11"], repo_root=site) == 1
    assert main(["--today", "2026-11-11"], repo_root=site) == 0
    assert main(["--check", "--today", "2026-11-11"], repo_root=site) == 0


def test_repository_llms_lists_every_published_nav_page() -> None:
    root = Path(__file__).resolve().parent.parent
    text = render_llms(root)
    import tomllib

    from scripts.build_sitemap import is_draft, page_url
    from tests.test_nav import _nav_files

    config = tomllib.loads((root / "zensical.toml").read_text(encoding="utf-8"))
    base = config["project"]["site_url"]
    for rel in _nav_files(config["project"]["nav"]):
        if not is_draft(root / "docs" / rel):
            assert f"]({page_url(base, rel)})" in text, rel
