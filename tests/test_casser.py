"""Casser son API : des requêtes qui doivent être refusées.

headers_user est la clé des tests (conftest.py) : sans effet avant le sprint 1, nécessaire ensuite.
"""
import pytest

VALID = {
    "distance_km": 120.0, "poids_kg": 450.0, "heure_depart": 17,
    "pluie_mm": 8.0, "trafic_index": 7.5, "nb_arrets": 4, "type_vehicule": "camion",
}
SANS_POIDS = {k: v for k, v in VALID.items() if k != "poids_kg"}  # VALID sans une clé


CAS_REFUSES = [
    # (description, url, corps, code attendu)

    # 1. Valeur absurde : poids supérieur à 3500 kg
    ("valeur absurde", "/v1/predict", {**VALID, "poids_kg": 99999}, 422),

    # 2. Champ obligatoire manquant : poids_kg
    ("champ manquant", "/v1/predict", SANS_POIDS, 422),

    # 3. Mauvais type : texte au lieu d'un nombre
    ("mauvais type", "/v1/predict", {**VALID, "distance_km": "cent vingt"}, 422),

    # 4. Champ supplémentaire non autorisé
    ("champ supplémentaire", "/v1/predict", {**VALID, "nom_client": "Oussama"}, 422),

    # 5. Route inexistante
    ("mauvaise route", "/v1/predict-inexistant", VALID, 404),
]


@pytest.mark.parametrize("description, url, corps, attendu", CAS_REFUSES)
def test_requete_refusee(client, headers_user, description, url, corps, attendu):
    assert client.post(url, json=corps, headers=headers_user).status_code == attendu, description
