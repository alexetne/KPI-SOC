# KPI-SOC

KPI-SOC est une base de SOAR oriente gestion d'incidents, saisie d'alertes et production de KPI securite. Le premier palier produit une table dynamique facon tableur/admin SQL, puis des vues de requetage et des panneaux de reporting configurables.

## Objectif produit

- Centraliser des alertes et incidents securite dans une table flexible.
- Permettre d'ajouter, supprimer et typer des colonnes sans migration applicative lourde.
- Exposer une API OpenAPI pour interconnexion avec d'autres outils SOC/SIEM/SOAR.
- Construire une bibliotheque de KPI: volume d'alertes, conversion alerte vers incident, endpoints les plus bruyants, repartition par severite, delais de traitement.
- Composer des rapports et tableaux de bord reutilisables avec panneaux et graphiques.

## Architecture

```text
KPI-SOC
├── backend/      API Python FastAPI, OpenAPI, modele incident-table, KPI
├── frontend/     App Node/React/Vite, table dynamique, dashboard
├── infra/        Reverse proxy et configuration de deploiement
├── docs/         Decisions d'architecture et specifications fonctionnelles
└── scripts/      Scripts de confort dev/test/prod
```

## Environnements

- `dev` / `preview`: experience locale ou branche de previsualisation, CORS ouvert sur le frontend, reload actif.
- `test`: base isolee, donnees jetables, configuration stricte pour CI.
- `prod`: services durcis, variables obligatoires, reverse proxy Nginx.

Des exemples dedies sont disponibles dans `env/`.

## Demarrage rapide

```bash
cp .env.example .env
docker compose --profile dev up --build
```

Services par defaut:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- OpenAPI: http://localhost:8000/docs
- PostgreSQL: localhost:5432

## Scripts utiles

```bash
./scripts/dev.sh
./scripts/test.sh
./scripts/prod-smoke.sh
```

## Roadmap initiale

## Fonctionnalites MVP disponibles

- Seed SOC via l'interface ou `POST /api/v1/demo/seed`.
- Table dynamique avec colonnes typees et lignes JSONB.
- Ajout/suppression de colonnes avec nettoyage des valeurs associees.
- Ajout/suppression de lignes depuis l'interface.
- Requetes directes avec recherche globale, filtre colonne/valeur et pagination.
- Catalogue de KPI mappables sur les colonnes.
- Panneaux KPI: volume, conversion, endpoint le plus bruyant, severite, statut, tendance, temps moyen de cloture.
- Configuration d'import Sekoia: mapping des champs de `/v1/sic/alerts` vers les colonnes de la table, avec conservation de la saisie manuelle.
- OpenAPI expose sous `/docs` et `/api/v1/openapi.json`.

## Mapping Sekoia

La section `Configuration` de l'interface permet de renseigner:

- l'URL API Sekoia, par defaut `https://api.sekoia.io`;
- un token API, envoye au backend uniquement au moment de l'import;
- une limite et des parametres query;
- le chemin JSON source pour chaque colonne du tableau.

Exemples de chemins utiles pour `/v1/sic/alerts`:

- `title` -> nom de l'alerte;
- `entity.name` -> endpoint ou entite;
- `urgency.display` -> severite;
- `status.name` -> statut;
- `created_at` -> date de creation.

## Prochaines etapes produit

1. Edition inline des cellules.
2. Sauvegarde de vues filtrees.
3. Dashboards persistants configurables par drag-and-drop.
4. Ordonnancement de rapports periodiques.
5. Connecteurs entrants/sortants via OpenAPI et webhooks.
6. Authentification, RBAC et audit trail.
