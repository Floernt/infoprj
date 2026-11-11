"""Génère ``overrides/llms.txt`` au format llmstxt.org.

Workflow:
    python scripts/build_llms.py [--check] [--today AAAA-MM-JJ]

Le fichier est la porte d'entrée des moteurs de réponse (ChatGPT, Perplexity,
Claude, AI Overviews) : un H1, un résumé en citation, puis des sections H2 de
liens ``- [titre](url): description``. Il est composé de :
    - une partie fixe, rédigée à la main dans ``data/llms-intro.md`` ;
    - une section par rubrique du menu (``nav`` de zensical.toml), dans l'ordre ;
    - la FAQ et les pages du pied de page ;
    - une section ``Optional`` avec les notes d'actualité publiées.

Exclus : pages ``draft: true`` et notes d'actualité programmées.
Le fichier est copié tel quel dans le site (pas de rendu Jinja) : aucun
en-tête de commentaire possible, d'où cet avertissement ici. Ne pas éditer
``overrides/llms.txt`` à la main.
Appelé automatiquement à la fin de ``inject_git_dates.py`` et par le déploiement.
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_actualites import md_text, page_title, split_front_matter  # noqa: E402
from build_sitemap import NOTES_PREFIX, is_draft, is_scheduled, page_url  # noqa: E402


FAQ = "faq/README.md"
# Pages du pied de page, dans l'ordre d'affichage.
FOOTER_PAGES = [
    "delais.md",
    "chiffres.md",
    "glossaire.md",
    "ressources.md",
    "a-propos.md",
    "contact.md",
]


def _description(meta: dict) -> str:
    text = meta.get("description") or meta.get("resume") or ""
    return re.sub(r"\s+", " ", str(text)).strip()


class _Site:
    def __init__(self, repo_root: Path, today: str) -> None:
        self.docs = repo_root / "docs"
        self.today = today
        config = tomllib.loads((repo_root / "zensical.toml").read_text(encoding="utf-8"))
        self.base = config["project"]["site_url"]
        self.nav = config["project"].get("nav", [])

    def published(self, rel: str) -> bool:
        file = self.docs / rel
        return (
            file.is_file()
            and not is_draft(file)
            and not is_scheduled(rel, file, self.today)
        )

    def item(self, rel: str, title: str | None = None) -> str:
        meta, _ = split_front_matter((self.docs / rel).read_text(encoding="utf-8"))
        title = title or page_title(self.docs, rel)
        line = f"- [{md_text(title)}]({page_url(self.base, rel)})"
        description = _description(meta)
        return f"{line}: {description}" if description else line


def _nav_entries(items) -> list[tuple[str | None, str]]:
    """(libellé du menu ou None pour une page d'entrée, fichier), à plat."""
    entries: list[tuple[str | None, str]] = []
    for item in items:
        if isinstance(item, str):
            entries.append((None, item))
        elif isinstance(item, dict):
            for label, value in item.items():
                if isinstance(value, str):
                    entries.append((label, value))
                else:
                    entries.extend(_nav_entries(value))
    return entries


def _section(title: str, lines: list[str]) -> list[str]:
    return [f"## {title}", "", *lines, ""] if lines else []


def render_llms(repo_root: Path, today: str | None = None) -> str:
    site = _Site(repo_root, today or date.today().isoformat())
    intro_file = repo_root / "data" / "llms-intro.md"
    parts = [intro_file.read_text(encoding="utf-8").strip(), ""]

    for rubric in site.nav:
        for title, children in rubric.items():
            entries = _nav_entries([children] if isinstance(children, str) else children)
            lines = [site.item(rel, label) for label, rel in entries if site.published(rel)]
            parts += _section(title, lines)

    if site.published(FAQ):
        parts += _section("Questions fréquentes", [site.item(FAQ)])
    parts += _section(
        "Pages utiles", [site.item(rel) for rel in FOOTER_PAGES if site.published(rel)]
    )

    notes = sorted(
        (
            p.relative_to(site.docs).as_posix()
            for p in site.docs.glob("actualites/20*.md")
        ),
        reverse=True,
    )
    parts += _section(
        "Optional",
        [site.item(rel) for rel in notes if rel.startswith(NOTES_PREFIX) and site.published(rel)],
    )
    return "\n".join(parts).rstrip() + "\n"


def main(argv: list[str] | None = None, repo_root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description="Génère overrides/llms.txt.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Ne pas écrire ; exit 1 si llms.txt est désynchronisé.",
    )
    parser.add_argument(
        "--today",
        metavar="AAAA-MM-JJ",
        help="Date de référence pour exclure les notes programmées (défaut : aujourd'hui).",
    )
    args = parser.parse_args(argv)

    repo_root = repo_root or Path.cwd()
    target = repo_root / "overrides" / "llms.txt"
    content = render_llms(repo_root, args.today)
    current = target.read_text(encoding="utf-8") if target.exists() else None
    if current == content:
        print("llms.txt à jour.")
        return 0
    if args.check:
        print("llms.txt à régénérer : overrides/llms.txt", file=sys.stderr)
        return 1
    target.write_text(content, encoding="utf-8", newline="\n")
    print("llms.txt régénéré : overrides/llms.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
