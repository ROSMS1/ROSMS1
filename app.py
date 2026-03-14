import streamlit as st
import math

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="ROSMS1 Expert", page_icon="⚡", layout="centered")

# Style pour ajuster la police sur mobile
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 18px; /* Taille moyenne adaptée aux smartphones */
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE DE CALCUL ---
def dimensionnement_hybride(i_site, p_panneau, capa_bat, v_syst):
    # 1. Calcul des Batteries & Autonomie
    # On considère une décharge sécurisée de 70% (DOD 70%)
    autonomie_h = (capa_bat * 0.7) / i_site if i_site > 0 else 0
    
    # 2. Courant de recharge batterie (10% de la capacité)
    i_recharge = capa_bat * 0.1
    
    # 3. Nombre de Panneaux (Besoin de couvrir Charge + Recharge)
    i_total_besoin = i_site + i_recharge
    p_solaire_necessaire = i_total_besoin * v_syst
    nb_panneaux = math.ceil(p_solaire_necessaire / p_panneau) if p_panneau > 0 else 0
    
    # 4. Capacité du Groupe Électrogène (GE)
    # Puissance apparente (kVA) = (P_watt / cos phi 0.8) + 30% de marge
    p_redresseur_kw = (i_total_besoin * v_syst) / 1000
    kva_ge = math.ceil((p_redresseur_kw / 0.8) * 1.3)
    
    # 5. Section Câble Batterie (Densité de courant 4A/mm2 pour sécurité)
    # Pour les batteries, on prend souvent le courant de recharge max ou de décharge
    i_max_bat = max(i_site, i_recharge)
    section_bat = next((s for s in [16, 25, 35, 50, 70, 95] if s >= i_max_bat / 4), 120)
    
    return nb_panneaux, kva_ge, autonomie_h, section_bat

# --- INTERFACE UTILISATEUR ---
st.title("🔋 Expert Hybride ROSMS1")
st.write("Entrez les données du site pour obtenir les recommandations.")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        i_site = st.number_input("Charge Site (Ampères)", value=40.0, step=1.0)
        capa_bat = st.number_input("Capacité Batterie (Ah)", value=600, step=100)
    with col2:
        p_panneau = st.number_input("Puissance Panneau (Wc)", value=450, step=10)
        v_syst = st.selectbox("Tension Système (V)", [48, 24, 12])

if st.button("Générer les Recommandations"):
    nb_p, ge_kva, auto, sect = dimensionnement_hybride(i_site, p_panneau, capa_bat, v_syst)
    
    st.divider()
    st.subheader("📋 Recommandations Techniques")
    
    c1, c2 = st.columns(2)
    c1.metric("Panneaux Solaires", f"{nb_p} unités")
    c2.metric("Groupe Électrogène", f"{ge_kva} kVA")
    
    c3, c4 = st.columns(2)
    c3.metric("Autonomie Estimée", f"{auto:.1f} Heures")
    c4.metric("Câble Batterie", f"{sect} mm²")
    
    st.info(f"Note : L'autonomie est calculée pour une décharge de 70% de vos {capa_bat}Ah.")
