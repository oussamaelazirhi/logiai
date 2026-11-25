# ADR 003 : sécurité de l'API LogiAI

## Décision 1 : où transmettre la clé (en-tête, URL ou corps) ?

- **Notre choix :** Transmettre la clé API dans l'en-tête HTTP `X-API-Key`.

- **Ce que l'autre option ferait perdre :**
  - **URL :** La clé pourrait apparaître dans les historiques du navigateur, les journaux des serveurs ou les URLs partagées, ce qui augmente le risque de fuite.
  - **Corps de la requête :** La clé serait mélangée aux données métier envoyées à l'API, ce qui rendrait son utilisation moins standard et moins pratique pour les requêtes qui n'ont pas de corps, comme les requêtes GET.

L'en-tête HTTP permet de séparer les informations d'authentification des données métier et facilite la gestion de la sécurité.

## Décision 2 : quelles origines autoriser (CORS) ? Une liste précise ou « * » ?

- **Notre choix :** Utiliser une liste précise d'origines autorisées :
  - `http://localhost:5500`
  - `http://127.0.0.1:5500`

- **Ce que l'autre option ferait perdre :**
  - **« * » :** Autoriser toutes les origines permettrait à n'importe quel site web d'effectuer des requêtes depuis un navigateur vers notre API. Cela élargirait inutilement la surface d'exposition.

Une liste précise limite les origines autorisées aux interfaces de développement prévues pour LogiAI et réduit les risques liés aux accès depuis des sites non autorisés.
