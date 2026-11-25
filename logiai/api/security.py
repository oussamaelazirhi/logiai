"""Authentification par clé d'API : qui êtes-vous ? et avez-vous le droit ?"""

import secrets

from fastapi import Depends, Header, HTTPException

from logiai import config


def _egal(a: str | None, b: str | None) -> bool:
    """Comparaison en temps constant. Une clé non configurée n'est jamais valide."""
    if not a or not b:
        return False
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def verify_api_key(x_api_key: str | None = Header(default=None)) -> str:
    """Authentification : renvoie le rôle ('user' ou 'admin') ou lève une 401."""

    # 1. Vérifier si la clé API est absente
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Clé API manquante",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # 2. Vérifier si la clé correspond à celle de l'administrateur
    if _egal(x_api_key, config.ADMIN_KEY):
        return "admin"

    # 3. Vérifier si la clé correspond à celle d'un utilisateur
    if _egal(x_api_key, config.API_KEY):
        return "user"

    # 4. Si aucune clé ne correspond
    raise HTTPException(
        status_code=401,
        detail="Clé API invalide",
        headers={"WWW-Authenticate": "ApiKey"},
    )


def require_admin(role: str = Depends(verify_api_key)) -> str:
    """Autorisation : réservé aux administrateurs."""

    # Vérifier si l'utilisateur possède le rôle administrateur
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux administrateurs",
        )

    return role