# Compte rendu : TP API LogiAI

**Noms : Oussama El Azirhi**   **Groupe :** ........

## 1. Environnement et premiers tests
- Sortie de `python -m pytest` au départ (collez-la) :
er> python -m pytest
=================================== test session starts ===================================
platform win32 -- Python 3.14.3, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\oussama\Desktop\5IA\Dévelopment d'applications intelligente\atelier3\starter
plugins: anyio-4.15.1
- Pourquoi certains tests qui attendent un 422 passent-ils déjà, alors que rien n'est écrit ?
Parce que la validation de la structure, du type et des contraintes des données est gérée automatiquement en amont par Pydantic dans le schéma Livraison. Dès qu'une requête arrive avec un format invalide, FastAPI rejette la requête avec un code 422 Unprocessable Entity avant même que la logique de la fonction ne soit exécutée.

## 2. Mon schéma
- Mes bornes et leur justification physique (une ligne par variable) :

| Variable | Min | Max | Pourquoi |
|---|---|---|---|
| distance_km | 1 | 1000 | Une livraison locale fait au minimum 1 km et dépasse rarement 1000 km pour un service standard.|
| poids_kg | 0.1| 5000|Représente des colis allant d'un petit paquet léger jusqu'à une charge lourde de transport. |
| heure_depart |0 |23 | Correspond aux 24 heures d'une journée (format horaire 00h00 - 23h59). |
| pluie_mm | 0| 200| Quantité de pluie en mm, de zéro (temps sec) jusqu'à des intempéries extrêmes.|
| trafic_index |1 |10 |Indice de congestion normalisé allant d'une circulation fluide (1) à un blocage total (10). |
| nb_arrets |0 |50 |Nombre d'arrêts intermédiaires possibles sur une tournée de livraison. |

## 3. Ma fonction predict()
@app.post("/v1/predict", response_model=PredictionOut)
def predict(livraison: Livraison, request: Request):
    """Évalue le risque de retard pour une livraison donnée."""
    predictor = state.get("predictor")
    
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Veuillez entraîner le modèle avec 'python -m logiai.train'."
        )
    
    resultat = predictor.predict(livraison.model_dump())
    return PredictionOut(**resultat)

## 4. Quatre requêtes
| Requête | Code obtenu | Pourquoi |
|---|---|---|
| livraison normale | 200 OK| Les données sont valides, le modèle est chargé et retourne la prédiction.|
| distance_km = -5 | 422 Unprocessable Entity| Pydantic bloque la valeur car elle ne respecte pas la contrainte de borne minimale (ge=0 ou positif).|
| type_vehicule = "avion" |422 Unprocessable Entity | Le véhicule n'est pas inclus dans la liste autorisée (Literal["moto", "voiture", "camion"]).|
| modèle absent (supprimez models/ et relancez) |503 Service Unavailable | Le modèle n'est pas trouvé dans l'état de l'application, déclenchant explicitement l'exception 503.|

## 5. Questions de compréhension
1. Pourquoi charge-t-on le modèle au démarrage et pas à chaque requête ?
   Charger un modèle de Machine Learning depuis le disque dur (joblib.load) est une opération coûteuse en temps et en ressources. Le charger une seule fois dans l'événement lifespan et le stocker en mémoire RAM garantit des temps de réponse instantanés pour chaque requête.
2. Qui écrit le contrôle « pluie <= 100 », et où est-il écrit ?
   Il est écrit par le développeur dans le schéma Pydantic (schemas.py) via les validateurs ou les arguments de validation de type Field.
3. Différence entre 422 et 503 ?
   422 indique une erreur de validation de la requête du client (données incorrectes).

   503 indique que le serveur fonctionne mais qu'il est incapable de traiter la demande car une ressource critique (le modèle ML) est absente ou non initialisée.
4. Pourquoi une route `/v1/predict` plutôt que `/predict` ?
   Pour assurer le versioning de l'API. Cela permet de modifier ou d'améliorer l'API à l'avenir (en créant un /v2/predict) sans casser la compatibilité avec les clients existants.
5. Que se passerait-il si la distance était déclarée `int` ?
   Les distances comportant des décimales précises (ex: 12.5 km) seraient soit rejetées, soit tronquées, ce qui nuirait à la précision des calculs du modèle de Machine Learning.

## 6. Décision : modèle absent
Répondre 503 ou refuser de démarrer ? Qu'est-ce que chaque option fait perdre ?
Répondre 503 : Permet à l'API de démarrer correctement (les routes de diagnostic comme /health restent accessibles), mais avertit proprement l'utilisateur que le service de prédiction est temporairement indisponible.

Refuser de démarrer : L'application plante dès le lancement si le fichier de modèle est absent.

Ce que chaque option fait perdre : Répondre 503 offre une meilleure résilience (l'API ne tombe pas complètement), tandis que refuser de démarrer évite d'exposer une application partiellement non fonctionnelle mais bloque l'accès à toute l'interface.

## 7. Lien de la pull request
https://github.com/oussamaelazirhi/logiai/pull/new/tp-api