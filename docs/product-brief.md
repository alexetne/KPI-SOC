# Brief Produit

## Vision

KPI-SOC doit devenir un socle SOAR leger centre sur l'exploitation d'incidents et la production d'indicateurs. L'ambition n'est pas de remplacer un SIEM au depart, mais de donner une couche operationnelle flexible ou une equipe SOC peut saisir, qualifier, filtrer, enrichir et mesurer ses alertes.

## Personas

- Analyste SOC: saisit, filtre, enrichit et qualifie les alertes.
- Incident manager: suit les conversions, les delais et la priorisation.
- Responsable securite: consulte les tendances, les metriques et rapports.
- Integrateur: connecte KPI-SOC a des outils tiers via OpenAPI.

## MVP

- Une table principale configurable.
- Colonnes typables: texte, nombre, booleen, date, enum, severite, utilisateur, endpoint, statut.
- Lignes CRUD.
- Filtres simples et tri.
- KPI preconfigures mappes sur les colonnes.
- Dashboard avec panneaux modifiables.
- Export JSON/CSV et API documentee.

## KPI Cibles

- Nombre d'alertes sur une periode.
- Nombre d'incidents confirmes sur une periode.
- Taux de conversion alerte vers incident.
- Endpoint le plus generateur d'alertes.
- Repartition par severite.
- Repartition par statut.
- Temps moyen entre creation, qualification et cloture.
- Top sources, top categories, top analystes.

## Hypotheses Structurantes

- Le modele de colonnes evolue souvent, donc les valeurs de lignes sont stockees en JSONB.
- Les colonnes restent decrites dans une table de schema pour valider et documenter les donnees.
- Les KPI sont definis comme des templates reutilisables plutot que du code dur partout dans l'interface.
- Les integrations externes consomment l'API REST documentee par OpenAPI.
