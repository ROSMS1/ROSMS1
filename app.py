import streamlit as st
import math

# --- CONFIGURATION & PWA ---
st.set_page_config(page_title="ROSMS1", page_icon="static/logo.png")

st.markdown("""
    <link rel="manifest" href="/static/manifest.json">
    <link rel="apple-touch-icon" href="/static/logo.png">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

# --- FONCTIONS DE CALCUL ---
def calc_cable(i_tot, longueur, v=48):
    rho = 0.0175
    s_chute = (2 * rho * longueur * i_tot) / (v * 0.03)
    data_cables = {1.5:15, 2.5:21, 4:28, 6:36, 10:50, 16:68, 25:89, 35:110, 50:134, 70:171, 95:210, 120:240}
    s_retenue = next((s for s in sorted(data_cables.keys()) if s >= s_chute and data_cables[s] >= i_tot), 120)
    calibres = [10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250]
    dj = next((c for c in calibres if c > i_tot), 250)
    return s_retenue, dj

# --- INTERFACE PRINCIPALE ---
st.title("🔋 Expert Télécom Hybride v2")
st.sidebar.header("Configuration du Site")
mode = st.sidebar.radio("Choisir l'option :", ["Bilan de Charge Simple", "Dimensionnement Hybride Solaire"])

# --- OPTION 1 : BILAN DE CHARGE SIMPLE ---
if mode == "Bilan de Charge Simple":
    st.header("📋 Bilan de Charge & Protection")
    col1, col2 = st.columns(2)
    with col1:
        i_charge = st.number_input("Charge Totale (Amperès A)", value=40.0)
        longueur = st.number_input("Longueur Câble (mètres)", value=10)
    
    s, dj = calc_cable(i_charge, longueur)
    
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Section Câble Recommandée", f"{s} mm²")
    c2.metric("Calibre Disjoncteur", f"{dj} A")

# --- OPTION 2 : SITE HYBRIDE ---
else:
    st.header("☀️ Dimensionnement Site Hybride")
    
    with st.expander("📥 Données d'entrée", expanded=True):
        c1, c2 = st.columns(2)
        i_site = c1.number_input("Charge Site (A)", value=50.0)
        p_panneau = c2.number_input("Puissance d'un Panneau (Wc)", value=450)
        capa_bat = c1.number_input("Capacité Batterie (Ah)", value=600)
        v_syst = c2.selectbox("Tension Système (V)", [48, 24, 12])

    # Calculs Hybrides
    # 1. Puissance Redresseur (Charge + Recharge Batterie à 10%)
    i_recharge = capa_bat * 0.1
    i_total_redresseur = i_site + i_recharge
    p_redresseur_kw = (i_total_redresseur * v_syst) / 1000

    # 2. Groupe Électrogène (GE) - Sécurité de 30% incluse
