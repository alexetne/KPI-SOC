# Architecture Technique

## Backend

- Python 3.12
- FastAPI pour l'API REST et OpenAPI native
- SQLAlchemy 2.x
- PostgreSQL avec JSONB
- Pydantic Settings pour les environnements
- Pytest pour les tests

## Frontend

- Node 20
- React + TypeScript + Vite
- TanStack Table pour la table dynamique
- Recharts pour les graphiques KPI
- Axios pour le client API

## Donnees

Le coeur est compose de quatre concepts:

- `tables`: un espace logique de saisie, par exemple `security_alerts`.
- `columns`: le schema dynamique d'une table.
- `rows`: les lignes, stockees en JSONB.
- `dashboard_panels`: les panneaux de reporting configurables.

## API

L'API est versionnee sous `/api/v1`.

Principales ressources:

- `/api/v1/tables`
- `/api/v1/tables/{table_id}/columns`
- `/api/v1/tables/{table_id}/rows`
- `/api/v1/kpis/definitions`
- `/api/v1/kpis/query`
- `/api/v1/dashboards`

## Deploiement

- Dev/preview: Docker Compose avec reload.
- Test: services identiques, base separee et tests automatises.
- Prod: images construites, Nginx en frontal, variables explicites.
