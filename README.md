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

1. Table dynamique avec colonnes typees et lignes JSONB.
2. Requetes directes avec filtres simples.
3. Catalogue de KPI mappables sur les colonnes.
4. Dashboards facon Grafana avec panneaux configurables.
5. Ordonnancement de rapports periodiques.
6. Connecteurs entrants/sortants via OpenAPI et webhooks.
