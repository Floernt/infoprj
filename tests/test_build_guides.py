"""Tests de la publication programmée des guides."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.build_guides import load_guides, main, validate

NAV = """[project]
site_url = "https://example.be/"
nav = [
  { "Guides" = [
    "guides/README.md",
    { "Publié" = "guides/publie.md" },
    { "Programmé" = "guides/programme.md" },
  ] },
]
"""


def _site(tmp_path: Path, extra: dict[str, str] | None = None) -> Path:
    (tmp_path / "zensical.toml").write_text(NAV, encoding="utf-8")
    pages = {
        "guides/README.md": (
            "# Guides\n\n<div class=\"ifa-subtiles\" markdown>\n"
            "[**Publié** Texte.](publie.md){ .ifa-subtile }\n"
            "[**Programmé** Texte.](programme.md){ .ifa-subtile }\n"
            "</div>\n"
        ),
        "guides/publie.md": "---\ndate: '2026-11-11'\n---\n# Publié\n",
        "guides/programme.md": "---\ndate: '2026-12-01'\n---\n# Programmé\n\n[Voir](publie.md)\n",
        "creanciers/README.md": (
            "# Créanciers\n\n[**Guide** Texte.](../guides/programme.md){ .ifa-subtile }\n"
            "[**Autre** Texte.](vote.md){ .ifa-subtile }\n"
        ),
    }
    pages.update(extra or {})
    for rel, content in pages.items():
        path = tmp_path / "docs" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp_path


def test_scheduled_guides_are_those_dated_after_today(tmp_path: Path) -> None:
    site = _site(tmp_path)
    guides = load_guides(site / "docs")
    assert {g.slug: g.date for g in guides} == {"publie": "2026-11-11", "programme": "2026-12-01"}
    assert [g.slug for g in guides if g.date > "2026-11-12"] == ["programme"]


def test_missing_date_is_an_error(tmp_path: Path) -> None:
    site = _site(tmp_path, {"guides/sans-date.md": "---\ndescription: x\n---\n# X\n"})
    with pytest.raises(ValueError, match="sans-date.md"):
        load_guides(site / "docs")


def test_tiles_pointing_to_a_scheduled_guide_are_allowed(tmp_path: Path) -> None:
    site = _site(tmp_path)
    assert validate(site / "docs", load_guides(site / "docs"), "2026-11-12") == []


def test_body_link_to_a_scheduled_guide_is_refused(tmp_path: Path) -> None:
    site = _site(tmp_path, {"comprendre/sursis.md": "# Sursis\n\nVoir [le guide](../guides/programme.md).\n"})
    errors = validate(site / "docs", load_guides(site / "docs"), "2026-11-12")
    assert len(errors) == 1 and "comprendre/sursis.md" in errors[0]


def test_later_guide_may_link_to_an_earlier_scheduled_guide(tmp_path: Path) -> None:
    site = _site(
        tmp_path,
        {"guides/plus-tard.md": "---\ndate: '2027-01-05'\n---\n# Plus tard\n\n[Voir](programme.md#etape-1)\n"},
    )
    assert validate(site / "docs", load_guides(site / "docs"), "2026-11-12") == []


def test_no_error_once_the_date_is_reached(tmp_path: Path) -> None:
    site = _site(tmp_path, {"comprendre/sursis.md": "# Sursis\n\n[Guide](../guides/programme.md)\n"})
    assert validate(site / "docs", load_guides(site / "docs"), "2026-12-01") == []


def test_drop_future_removes_file_tiles_and_nav_line(tmp_path: Path) -> None:
    site = _site(tmp_path)
    assert main(["--drop-future", "--today", "2026-11-12"], repo_root=site) == 0
    docs = site / "docs"
    assert not (docs / "guides" / "programme.md").exists()
    assert (docs / "guides" / "publie.md").exists()
    assert "programme.md" not in (docs / "guides" / "README.md").read_text(encoding="utf-8")
    assert "publie.md" in (docs / "guides" / "README.md").read_text(encoding="utf-8")
    creanciers = (docs / "creanciers" / "README.md").read_text(encoding="utf-8")
    assert "programme.md" not in creanciers and "vote.md" in creanciers
    toml = (site / "zensical.toml").read_text(encoding="utf-8")
    assert "guides/programme.md" not in toml and "guides/publie.md" in toml


def test_drop_future_keeps_everything_on_publication_day(tmp_path: Path) -> None:
    site = _site(tmp_path)
    assert main(["--drop-future", "--today", "2026-12-01"], repo_root=site) == 0
    assert (site / "docs" / "guides" / "programme.md").exists()
    assert "guides/programme.md" in (site / "zensical.toml").read_text(encoding="utf-8")


def test_check_fails_on_invalid_reference(tmp_path: Path) -> None:
    site = _site(tmp_path, {"comprendre/sursis.md": "# Sursis\n\n[Guide](../guides/programme.md)\n"})
    assert main(["--check", "--today", "2026-11-12"], repo_root=site) == 2
    assert (site / "docs" / "guides" / "programme.md").exists()
