"""Application principale FastAPI pour LogiAI."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from logiai import predict as predictor_module
from logiai.api.schemas import Livraison, PredictionOut
from logiai.config import MODEL_PATH

# État global de l'application attendu par les tests (state)
state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge le modèle au démarrage de l'application."""
    try:
        # On essaie d'initialiser le prédicateur selon la structure du starter
        if hasattr(predictor_module, "DeliveryPredictor"):
            predictor = predictor_module.DeliveryPredictor(MODEL_PATH)
        elif hasattr(predictor_module, "load_model"):
            predictor = predictor_module.load_model(MODEL_PATH)
        else:
            predictor = predictor_module.Predictor(MODEL_PATH)
        state["predictor"] = predictor
    except (FileNotFoundError, OSError, ValueError, AttributeError):
        state["predictor"] = None
    yield
    state.clear()


app = FastAPI(title="LogiAI API", version="1.0", lifespan=lifespan)


@app.get("/health")
def health():
    """Vérifie l'état de santé de l'API et si le modèle est chargé."""
    loaded = state.get("predictor") is not None
    return {"status": "ok", "model_loaded": loaded}


@app.post("/v1/predict", response_model=PredictionOut)
def predict(livraison: Livraison, request: Request):
    """Évalue le risque de retard pour une livraison donnée."""
    # 1. Récupérer le prédicateur stocké dans state
    predictor = state.get("predictor")

    # 2. Si le modèle est absent, renvoyer une erreur 503
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Veuillez entraîner le modèle avec 'python -m logiai.train'.",
        )

    # 3. Effectuer la prédiction avec le modèle
    if hasattr(predictor, "predict"):
        resultat = predictor.predict(livraison.model_dump())
    else:
        resultat = predictor(livraison.model_dump())

    # 4. Retourner le résultat validé par PredictionOut
    return PredictionOut(**resultat)