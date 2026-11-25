
"""L'API LogiAI : python -m uvicorn logiai.api.main:app --reload"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from logiai import config
from logiai.api.schemas import Livraison, PredictionOut
from logiai.api.security import require_admin, verify_api_key
from logiai.predict import Predictor

state: dict = {}  # Contient le predictor une fois le modèle chargé


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Exécuté une seule fois au démarrage du serveur
    if config.MODEL_PATH.exists():
        state["predictor"] = Predictor(config.MODEL_PATH)

    yield

    # Nettoyage à l'arrêt du serveur
    state.clear()


app = FastAPI(
    title="LogiAI",
    version="1.1.0",
    description="Prédit le risque de retard d'une livraison. Authentification : en-tête X-API-Key.",
    lifespan=lifespan,
)


# Configuration CORS : autoriser le frontend à communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.get("/health")
def health():
    """Route publique : ne nécessite aucune clé API."""
    return {
        "status": "ok",
        "model_loaded": "predictor" in state,
        "auth_configured": bool(config.API_KEY and config.ADMIN_KEY),
    }


@app.post(
    "/v1/predict",
    response_model=PredictionOut,
    dependencies=[Depends(verify_api_key)],
)
def predict(livraison: Livraison):
    """Prédit le risque de retard. Nécessite une clé API valide."""
    predictor = state.get("predictor")

    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé : lancez 'python -m logiai.train' puis redémarrez l'API.",
        )

    return PredictionOut(**predictor.predict(livraison.model_dump()))


@app.get(
    "/v1/model-info",
    dependencies=[Depends(require_admin)],
)
def model_info():
    """Informations sur le modèle : réservé à l'administrateur."""
    predictor = state.get("predictor")

    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé.",
        )

    return {
        "version": predictor.version,
        "seuil": predictor.threshold,
        "variables": config.FEATURES,
    }
