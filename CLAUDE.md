# CLAUDE.md — infoprj

Notes de contexte pour Claude. À mettre à jour quand le projet évolue.

## Projet

Site documentaire **La réorganisation judiciaire en Belgique** (infoprj.be), site frère d'[infofaillite.be](https://infofaillite.be/), basé sur le Livre XX du Code de droit économique tel que réformé au 1er septembre 2023. Public visé : dirigeants d'entreprises en difficulté, créanciers, professionnels du chiffre (experts-comptables, réviseurs).

- Stack : **Zensical** (statique, dérivé de MkDocs Material). Config dans [zensical.toml](zensical.toml).
- Sources Markdown : [docs/](docs/).
- Dépendances Python : [requirements.txt](requirements.txt), venv local dans `.venv/`.
- **Branches** (méthode identique à infofaillite) : `main` est la branche **publiée**, déployée automatiquement par GitHub Actions ([deploy.yml](.github/workflows/deploy.yml)) sur GitHub Pages à chaque push. **On travaille en local sur `gh-pages`**, on pousse `gh-pages` sur GitHub, puis Florian publie par une pull request `gh-pages` → `main`. Ne jamais commiter ni pousser directement sur `main`. Dépôt : `Floernt/infoprj`. Domaine : [docs/CNAME](docs/CNAME).
- L'architecture technique est reprise d'infofaillite (préfixe CSS `ifa-` conservé à dessein, pour pouvoir porter les améliorations d'un site à l'autre). Le clone de référence d'infofaillite se trouve, non suivi, dans [infofaillite/](infofaillite/) : ne pas le modifier depuis ce projet.

## Dossiers hors publication (ignorés par Git)

- `Ressources InfoPrj/` : supports de formation, présentations et textes de tiers servant de matière première. Ne jamais les commiter (droits d'auteur de tiers).
- `sources/brouillons/` : les cinq brouillons initiaux de Florian, redistribués dans les pages du site.
- `infofaillite/` : clone du site frère.
- `.git-ancien-infofaillite/` : ancien dépôt Git de ce dossier (clone d'infofaillite), mis de côté lors de la création ; peut être supprimé.

## Arborescence éditoriale

- [docs/README.md](docs/README.md) — accueil (`template: home.html`), entrée par profil.
- [docs/dirigeants/](docs/dirigeants/) — parcours du dirigeant : signaux d'alarme, choix de la voie, chambre des entreprises en difficulté, préparation, plan, après l'homologation, responsabilité, échec.
- [docs/creanciers/](docs/creanciers/) — parcours du créancier : débiteur en PRJ, créanciers sursitaires, vote, levée du sursis, initiative, classes, signaux.
- [docs/chiffre/](docs/chiffre/) — parcours du professionnel du chiffre : alerte XX.23 §3, continuité et procédure d'alarme du CSA, chambre, valorisation, plan d'affaires, comptabilité et fiscalité des abandons, check-list.
- [docs/comprendre/](docs/comprendre/) — règles de fond : définition, boîte à outils, réforme 2023, PRJ publique, sursis, PRJ privée, accords, grandes entreprises et classes, meilleur intérêt et cram-down, transfert et autres issues, acteurs.
- [docs/faq/README.md](docs/faq/README.md) — FAQ unique : blocs `<details class="ifa-faq" id="…" data-profils="dirigeant creancier chiffre" markdown>` sous des H2 de thème à ancre explicite ; filtres dans [docs/javascripts/faq.js](docs/javascripts/faq.js). JSON-LD `FAQPage` généré par [scripts/build_faq.py](scripts/build_faq.py).
- Front matter `public: [dirigeant, creancier, chiffre]` : affiché dans le bandeau (« Cette page concerne »), libellés dans [overrides/main.html](overrides/main.html).
- Pages hors menu (pied de page) : [glossaire](docs/glossaire.md), [délais](docs/delais.md), [chiffres](docs/chiffres.md), [ressources](docs/ressources.md), [à propos](docs/a-propos.md), [contact](docs/contact.md).
- [docs/actualites/](docs/actualites/) — notes d'actualité, une par fichier `AAAA-MM-JJ-slug.md`. `README.md` et `themes.md` générés entre marqueurs.
- [data/themes.yml](data/themes.yml) — taxonomie des thèmes et rattachement aux pages du guide (non publiée).
- [docs/stylesheets/extra.css](docs/stylesheets/extra.css) — identité visuelle : palette « Fresh Greens » Hunter Green `#386641` (structure), Blushed Brick `#bc4749` (accent), Sage `#6a994e` (liens, assombri `#4a7232` pour le texte), Yellow Green `#a7c957` (touches, jamais du texte), Champagne Mist `#f2e8cf` (fonds doux) ; police Albert Sans. Variantes de tuiles : `ifa-tile--brick`, `--sage`, `--hunter`, `--lime`.
- [logo/](logo/) — logo info·prj généré par [logo/make_logo.py](logo/make_logo.py) (voir [logo/README.md](logo/README.md)).
- Statistiques (Clicky) : non activées tant qu'un identifiant propre au site n'a pas été créé (ne pas réutiliser celui d'infofaillite).

## Navigation

- Le menu est **explicite** : `nav` dans [zensical.toml](zensical.toml), six rubriques (Je dirige l'entreprise, Je suis créancier, Professionnel du chiffre, Comprendre la PRJ, Actualités, Questions fréquentes).
- **Toute nouvelle page de fond doit être ajoutée au `nav`**. [tests/test_nav.py](tests/test_nav.py) échoue sinon. Exceptions : l'accueil, les pages du pied de page et les notes d'actualité.
- Le **sitemap est statique**, généré par [scripts/build_sitemap.py](scripts/build_sitemap.py) dans [overrides/sitemap.xml](overrides/sitemap.xml), régénéré par `inject_git_dates.py`.
- Les pages d'entrée de rubrique ouvrent sur une grille `ifa-subtiles` : la tenir à jour quand une page est ajoutée.

## Actualités : publier une note

Procédure identique à infofaillite :

1. `python scripts/new_actualite.py "Titre" --type jurisprudence|doctrine|legislation|pratique --themes slug1,slug2 [--date AAAA-MM-JJ]` ; slugs dans [data/themes.yml](data/themes.yml).
2. Rédiger la note ; remplir ou supprimer les champs vides du front matter.
3. `python scripts/build_actualites.py` (`--check` pour vérifier sans écrire).
4. Commit éditorial, puis `inject_git_dates.py` et commit `lastmod`.

Règles : ne jamais éditer à la main le contenu entre `<!-- actualites:auto:start -->` et `<!-- actualites:auto:end -->` ; dates du front matter toujours entre guillemets, aucune valeur vide ; une note datée dans le futur n'apparaît nulle part avant sa date (le workflow reconstruit le site chaque matin à 05:00 UTC avec `--drop-future`).

## Conventions éditoriales

- **Langue** : français de Belgique, clair et accessible ; ligne éditoriale dans [docs/a-propos.md](docs/a-propos.md).
- **Référencement légal** : Livre XX du CDE ; citer les articles précis. Toute référence doit être vérifiée dans le texte consolidé (Justel) ; les affirmations non tranchées par les sources sont consignées dans [superpowers/points-a-verifier.md](superpowers/points-a-verifier.md) jusqu'à arbitrage par Florian.
- **Liens internes** : relatifs en `.md`, pas d'URL absolues vers infoprj.be.
- **Ancres internes** : Zensical slugifie les titres en ASCII ; en cas de doute, ancre explicite `## Titre { #ancre }`.
- **Admonitions** : syntaxe MkDocs (`!!! danger`, `!!! note`, `!!! warning`).
- **Front matter YAML** : `description` + `keywords` en tête de chaque page ; `updated` est géré par script.
- **Pas d'emojis** dans les pages éditoriales.

## Workflow

- Commits courts et descriptifs en français.
- **Journaliser** les modifications de fond dans [LOG.md](LOG.md) avec le préfixe `## [YYYY-MM-DD] <type> | <titre>`.
- **Avant chaque build ou commit de contenu** : `python scripts/inject_git_dates.py` (mode `--check` pour CI).
- Tests : `.venv/Scripts/python.exe -m pytest`.

## Passes éditoriales (relecture / enrichissement)

Mêmes règles qu'infofaillite : pas de spec ni de plan pour une passe de relecture ; modifier directement les Markdown ; une question ciblée seulement si la demande est vraiment ambiguë ; un commit court par modification cohérente ; après une passe multi-fichiers, `inject_git_dates.py` puis entrée dans [LOG.md](LOG.md), commités ensemble. Specs et plans des chantiers techniques : [superpowers/specs/](superpowers/specs/) et [superpowers/plans/](superpowers/plans/), **jamais sous `docs/`**.

### Procédure de clôture de session de relecture

1. `git status` + `git diff --stat`.
2. `git diff <fichier>` pour chaque page modifiée hors session.
3. Commits éditoriaux (un par page ou groupe cohérent).
4. `.venv/Scripts/python.exe scripts/inject_git_dates.py`.
5. Entrée `## [YYYY-MM-DD] edit | <titre>` en tête de [LOG.md](LOG.md).
6. Commit final `log + lastmod : relecture du <date>`.
7. `git log --oneline -10` ; ne pas pousser sauf demande explicite (push sur `gh-pages` uniquement ; la publication passe par la PR `gh-pages` → `main`).
