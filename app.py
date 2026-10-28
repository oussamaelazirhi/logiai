"""Application Streamlit pour LogiAI."""
import requests
import streamlit as st

st.set_page_config(
    page_title="LogiAI - Prédiction de Retard",
    page_icon="📦",
    layout="centered",
)

st.title("📦 LogiAI - Prédiction de Retard de Livraison")
st.markdown("Renseignez les détails de la livraison pour estimer le risque de retard.")

# Formulaire de saisie des caractéristiques
with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        distance_km = st.number_input("Distance (km)", min_value=1.0, value=50.0)
        poids_kg = st.number_input("Poids (kg)", min_value=0.1, value=15.0)
        heure_depart = st.slider("Heure de départ", min_value=0, max_value=23, value=10)

    with col2:
        pluie_mm = st.number_input("Pluie (mm)", min_value=0.0, value=0.0)
        trafic_index = st.slider("Indice de trafic (1 à 10)", min_value=1.0, max_value=10.0, value=3.0)
        nb_arrets = st.number_input("Nombre d'arrêts", min_value=0, value=2)

    type_vehicule = st.selectbox("Type de véhicule", ["moto", "voiture", "camion"])

    submit_button = st.form_submit_button(label="Prédire le risque")

# Lorsque l'utilisateur clique sur le bouton
if submit_button:
    # Payload à envoyer à l'API FastAPI
    payload = {
        "distance_km": distance_km,
        "poids_kg": poids_kg,
        "heure_depart": heure_depart,
        "pluie_mm": pluie_mm,
        "trafic_index": trafic_index,
        "nb_arrets": nb_arrets,
        "type_vehicule": type_vehicule,
    }

    try:
        # Appel de l'API FastAPI en local
        response = requests.post("http://127.0.0.1:8000/v1/predict", json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            prob = result.get("probabilite_retard", 0.0)
            alerte = result.get("alerte_retard", False)

            st.success("Prédiction effectuée avec succès !")
            
            # Affichage visuel du résultat
            st.metric(label="Probabilité de retard", value=f"{prob * 100:.1f} %")

            if alerte:
                st.warning("⚠️ **Alerte :** Risque élevé de retard ! Le dispatcher devrait être prévenu.")
            else:
                st.info("✅ **À l'heure :** Le trajet présente un risque faible de retard.")
        else:
            st.error(f"Erreur de l'API (Code {response.status_code}) : {response.text}")

    except requests.exceptions.ConnectionError:
        st.error("Impossible de se connecter à l'API FastAPI. Assurez-vous qu'elle est bien lancée sur http://127.0.0.1:8000.")