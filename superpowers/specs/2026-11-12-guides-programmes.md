# Spec — publication programmée des guides

Date : 2026-11-12. Demande de Florian : publier un guide par mois, en programmation automatique (choix fait parmi deux options ; l'autre était une publication manuelle mensuelle).

## Besoin

Les guides de `docs/guides/` sont rédigés à l'avance et fusionnés dans `main` en une seule PR. Chacun ne doit apparaître sur le site qu'à sa date, comme les notes d'actualité (reconstruction quotidienne à 05:00 UTC, `--drop-future`).

## Règles

- Chaque guide (`docs/guides/*.md`, hors `README.md`) porte `date: 'AAAA-MM-JJ'` : sa date de publication. Champ obligatoire, entre guillemets.
- Un guide est **programmé** si sa `date` est postérieure au jour de référence (`--today`, défaut aujourd'hui, fuseau Europe/Brussels en CI).
- Un guide programmé ne peut être référencé ailleurs dans `docs/` que :
  - par une **tuile** (ligne contenant `{ .ifa-subtile }`), qui sera retirée avant sa date ;
  - par un autre guide dont la date est postérieure ou égale à la sienne.
  Toute autre référence est une erreur de validation (le lien serait cassé jusqu'à la date).
- En local, rien ne change : le guide programmé reste visible dans `zensical serve`, pour la relecture.

## Mécanisme

- `scripts/build_guides.py [--check] [--today AAAA-MM-JJ] [--drop-future]`
  - valide le front matter et les références (exit 2 en cas d'erreur) ;
  - liste les guides programmés ;
  - avec `--drop-future` (CI uniquement) : supprime le fichier du guide, les lignes de tuile qui le visent dans `docs/**/*.md` et sa ligne de `nav` dans `zensical.toml`.
- `scripts/build_sitemap.py` : `is_scheduled` couvre aussi les guides (et donc `build_llms.py`, qui l'importe).
- `.github/workflows/deploy.yml` : `build_guides.py --drop-future` avant le sitemap et `llms.txt`.

## Calendrier retenu

| Date | Guide |
|---|---|
| 2026-11-11 | La PRJ privée en six étapes (déjà publié) |
| 2026-12-01 | Créancier : la PRJ publique en huit étapes |
| 2027-01-05 | La PRJ publique côté dirigeant |
| 2027-02-02 | Convoqué par la chambre des entreprises en difficulté |
| 2027-03-02 | Le transfert sous autorité de justice |

Premier mardi du mois (le 1er janvier étant férié, le guide de janvier passe au 5).

## Tests

`tests/test_build_guides.py` : détection des programmés, validation des références (tuile admise, lien de corps refusé, lien depuis un guide plus tardif admis), `--drop-future` (fichier, tuiles, ligne de `nav`), champ `date` manquant. `tests/test_build_sitemap.py` : guide programmé exclu.
