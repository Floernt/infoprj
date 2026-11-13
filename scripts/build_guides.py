"""Publication programmée des guides pas à pas.

Workflow:
    python scripts/build_guides.py [--check] [--today AAAA-MM-JJ] [--drop-future]

Chaque guide ``docs/guides/*.md`` (hors ``README.md``) porte une clé
``date: 'AAAA-MM-JJ'`` : sa date de publication. Un guide dont la date est
postérieure au jour de référence est « programmé ».

Le script :
    1. valide la présence et le format de ``date`` ;
    2. vérifie qu'un guide programmé n'est référencé ailleurs que par une tuile
       (ligne ``{ .ifa-subtile }``) ou par un guide publié à la même date ou
       plus tard : tout autre lien serait cassé jusqu'à sa date ;
    3. avec ``--drop-future`` (CI, avant le build), supprime le fichier du
       guide programmé, les tuiles qui le visent et sa ligne de ``nav`` dans
       ``zensical.toml``.

En local, sans ``--drop-future``, rien n'est modifié : le guide reste
visible dans ``zensical serve`` pour la relecture. Sitemap et ``llms.txt``
l'excluent déjà (``build_sitemap.is_scheduled``).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

GUIDES_DIR = "guides"
TILE_MARK = ".ifa-subtile"
_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n", re.DOTALL)
_ISO_DATE_RE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")


@dataclass(frozen=True)
class Guide:
    rel: str  # chemin relatif à docs/, ex. "guides/programme.md"
    slug: str
    date: str


def load_guides(docs_root: Path) -> list[Guide]:
    guides: list[Guide] = []
    errors: list[str] = []
    for path in sorted((docs_root / GUIDES_DIR).glob("*.md")):
        if path.name == "README.md":
            continue
        rel = path.relative_to(docs_root).as_posix()
        match = _FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
        meta = (yaml.safe_load(match.group(1)) or {}) if match else {}
        value = meta.get("date")
        if not isinstance(value, str) or not _ISO_DATE_RE.match(value):
            errors.append(f"{rel} : clé « date » absente ou invalide (attendu 'AAAA-MM-JJ' entre guillemets)")
            continue
        guides.append(Guide(rel=rel, slug=path.stem, date=value))
    if errors:
        raise ValueError("\n".join(errors))
    return guides


def _link_re(slug: str) -> re.Pattern[str]:
    """Lien Markdown vers le guide, en relatif depuis n'importe quelle page."""
    return re.compile(r"\]\((?:\.\./)*(?:" + GUIDES_DIR + r"/)?" + re.escape(slug) + r"\.md[#)]")


def _pages(docs_root: Path) -> list[Path]:
    return sorted(docs_root.rglob("*.md"))


def validate(docs_root: Path, guides: list[Guide], today: str) -> list[str]:
    by_rel = {g.rel: g for g in guides}
    errors: list[str] = []
    for guide in (g for g in guides if g.date > today):
        pattern = _link_re(guide.slug)
        for path in _pages(docs_root):
            rel = path.relative_to(docs_root).as_posix()
            if rel == guide.rel:
                continue
            source = by_rel.get(rel)
            if source and source.date >= guide.date:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if pattern.search(line) and TILE_MARK not in line:
                    errors.append(
                        f"{rel}:{number} renvoie à {guide.rel}, programmé le {guide.date} "
                        "(seule une tuile peut le viser avant sa date)"
                    )
    return errors


def _without_lines(text: str, predicate) -> str:
    lines = text.splitlines(keepends=True)
    return "".join(line for line in lines if not predicate(line))


def drop(repo_root: Path, guides: list[Guide]) -> None:
    docs_root = repo_root / "docs"
    for guide in guides:
        (docs_root / guide.rel).unlink()
        pattern = _link_re(guide.slug)
        for path in _pages(docs_root):
            text = path.read_text(encoding="utf-8")
            new = _without_lines(text, lambda l: TILE_MARK in l and pattern.search(l))
            if new != text:
                path.write_text(new, encoding="utf-8")
        toml = repo_root / "zensical.toml"
        text = toml.read_text(encoding="utf-8")
        toml.write_text(_without_lines(text, lambda l: f'"{guide.rel}"' in l), encoding="utf-8")


def main(argv: list[str] | None = None, repo_root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publication programmée des guides.")
    parser.add_argument("--check", action="store_true", help="Valider sans rien modifier.")
    parser.add_argument("--today", metavar="AAAA-MM-JJ", help="Date de référence (défaut : aujourd'hui).")
    parser.add_argument(
        "--drop-future",
        action="store_true",
        help="Retirer du build les guides programmés (CI, avant le build).",
    )
    args = parser.parse_args(argv)
    if args.today and not _ISO_DATE_RE.match(args.today):
        parser.error("--today attend une date AAAA-MM-JJ")
    today = args.today or date.today().isoformat()

    repo_root = repo_root or Path.cwd()
    docs_root = repo_root / "docs"
    try:
        guides = load_guides(docs_root)
    except ValueError as exc:
        print(f"Erreur de validation :\n{exc}", file=sys.stderr)
        return 2
    errors = validate(docs_root, guides, today)
    if errors:
        print("Erreur de validation :\n" + "\n".join(errors), file=sys.stderr)
        return 2

    scheduled = sorted((g for g in guides if g.date > today), key=lambda g: g.date)
    for guide in scheduled:
        print(f"Programmé le {guide.date} : {guide.rel}")
    if args.drop_future and not args.check and scheduled:
        drop(repo_root, scheduled)
        print(f"{len(scheduled)} guide(s) programmé(s) retiré(s) du build.")
    elif not scheduled:
        print("Aucun guide programmé.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
