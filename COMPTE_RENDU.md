# Compte rendu : tester, sécuriser et appeler l'API LogiAI

**Noms :** Oussama El Azirhi  
**Groupe :** G3

## 1. Casser son API (activité 1)

| Cas | Requête (corps ou URL) | Prévu | Obtenu |
|---|---|---|---|
| Champ manquant | `/v1/predict` sans le champ `poids_kg` | 422 Unprocessable Entity | 422 |
| Valeur absurde | `/v1/predict` avec `poids_kg = 99999` | 422 Unprocessable Entity | 422 |
| Texte au lieu d'un nombre | `/v1/predict` avec `distance_km = "cent vingt"` | 422 Unprocessable Entity | 422 |
| Champ en trop | `/v1/predict` avec un champ supplémentaire `nom_client` | 422 Unprocessable Entity | 422 |
| Mauvaise route | `/v1/predict-inexistant` | 404 Not Found | 404 |

- Une requête acceptée alors qu'elle devait être refusée ? Aucune parmi les cinq requêtes testées après la mise en place des vérifications.

Les cinq tests automatisés de cette activité ont réussi.

## 2. Les 2 bugs (activité 2)

| Bug | Test qui l'a révélé | Comportement avant | Correction |
|---|---|---|---|
| 1. Heure de départ | Test des limites de `heure_depart` | Les heures hors de l'intervalle autorisé pouvaient être acceptées | Ajout de `Field(ge=0, le=23)` |
| 2. Nombre d'arrêts | Test des limites de `nb_arrets` | Les nombres d'arrêts hors de l'intervalle autorisé pouvaient être acceptés | Ajout de `Field(ge=0, le=15)` |

- Sortie de `python -m pytest` à la fin de l'activité 2 : **27 tests réussis**.

## 3. La clé API (sprint 1)

- Ma fonction `verify_api_key()` :

```python
def _egal(a: str | None, b: str | None) -> bool:
    """Comparaison en temps constant. Une clé non configurée n'est jamais valide."""
    if not a or not b:
        return False
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def verify_api_key(x_api_key: str | None = Header(default=None)) -> str:
    """Authentification : renvoie le rôle ('user' ou 'admin') ou lève une 401."""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Clé API manquante",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    if _egal(x_api_key, config.ADMIN_KEY):
        return "admin"
    if _egal(x_api_key, config.API_KEY):
        return "user"
    raise HTTPException(
        status_code=401,
        detail="Clé API invalide",
        headers={"WWW-Authenticate": "ApiKey"},
    )
```

| Requête | Code obtenu |
|---|---|
| `/v1/predict` sans clé | 401 Unauthorized |
| `/v1/predict` fausse clé | 401 Unauthorized |
| `/v1/predict` clé utilisateur | 200 OK |
| `/v1/model-info` clé utilisateur | 403 Forbidden |
| `/v1/model-info` clé administrateur | 200 OK |
| `/health` sans clé | 200 OK |

- Preuve que `.env` n'est pas dans Git : [Ajouter ici la sortie réelle de `git status` après vérification.]

## 4. Le client web (sprint 2)

- Mon `fetch` : [Coller ici le code exact de la fonction `fetch` présente dans `web/index.html`.]

- Ce qui s'affiche :
  - Livraison normale : résultat de prédiction avec la probabilité de retard et l'alerte.
  - Pluie de 500 mm : [Compléter après avoir effectué ce test.]
  - Fausse clé : message indiquant que la clé API est absente ou invalide.

- Expérience CORS (page servie sur le port 5501) :
  - Résultat attendu : le navigateur bloque la requête car l'origine du port 5501 ne figure pas dans `ALLOWED_ORIGINS`.
  - La console F12 affiche une erreur de politique CORS.
  - `curl` fonctionne quand même car il n'applique pas la politique CORS du navigateur. CORS est une protection appliquée par les navigateurs, et non un mécanisme d'authentification du serveur.

- Où voyez-vous la clé dans F12 ?
  Dans les outils de développement, onglet Network (Réseau), en sélectionnant la requête `/v1/predict`, puis dans Request Headers, sous le nom `X-API-Key`.

## 5. Questions de compréhension

**1. Quelle différence entre 401, 403 et 422 ?**

- 401 Unauthorized : la clé API est absente ou invalide. L'utilisateur n'est pas authentifié.
- 403 Forbidden : l'utilisateur est authentifié, mais ne possède pas les autorisations nécessaires pour accéder à la ressource.
- 422 Unprocessable Entity : la requête est reçue, mais les données envoyées ne respectent pas les règles de validation.

**2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ?**

Pour éviter son exposition et son utilisation par des personnes non autorisées. Les clés sont stockées dans le fichier `.env`, qui est exclu de Git grâce au `.gitignore`. Le fichier `.env.example` sert de modèle sans contenir les véritables clés.

**3. Pourquoi comparer avec `compare_digest` plutôt qu'avec `==` ?**

`compare_digest` effectue une comparaison en temps constant afin de réduire les risques d'attaques par analyse du temps de réponse, contrairement à une comparaison classique avec `==`.

**4. Pourquoi `curl` fonctionne-t-il alors que la page du port 5501 est bloquée ?**

Parce que CORS est une règle appliquée par les navigateurs web. `curl` n'applique pas cette restriction et peut envoyer directement une requête HTTP au serveur. Cela ne signifie pas que la requête est authentifiée ou autorisée.

**5. Pourquoi la validation faite par le navigateur ne remplace-t-elle pas celle de l'API ?**

La validation côté navigateur améliore l'expérience utilisateur, mais elle peut être contournée. Un utilisateur peut envoyer directement une requête HTTP avec Postman, `curl` ou un autre programme. L'API doit donc toujours vérifier elle-même les données reçues.

## 6. Lien de la Pull Request

[À compléter après la création de la Pull Request sur GitHub.]
