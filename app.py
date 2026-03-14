import streamlit as st
import math

# --- Configuration de la Page ---
st.set_page_config(
    page_title="ROSMS1 Hybrid Expert v3",
    page_icon="📡",
    layout="centered"
)

# --- Style CSS optimisé pour smartphone ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #1e40af; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 8px 16px;
    }
    html, body, [class*="css"] { font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Constantes Techniques ---
RHO = 0.0175 
SECTIONS_STD = [10, 16, 25, 35, 50, 70, 95, 120, 150]
CALIBRES_DJ = [10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200]
AMPACITE_CABLE = {10: 50, 16: 68, 25: 89, 35: 110, 50: 134, 70: 171, 95: 210, 120: 240, 150: 280}

# Liste des batteries suggérées (Nom: [Tension_Unitaire, Capacité_Ah])
DICT_BATTERIES = {
    "2V / 800Ah (OPzV)": [2, 800],
    "12V / 200Ah (Gel)": [12, 200],
    "2V / 1000Ah (Industriel)": [2, 1000],
    "48V / 200Ah (Lithium/Pack)": [48, 200]
}

def main():
    st.title("📡 ROSMS1 Hybrid Expert")

    tab1, tab2 = st.tabs(["📊 Dimensionnement", "⚡ Câblage & Sécurité"])

    # ---------------------------------------------------------
    # INTERFACE 1 : DIMENSIONNEMENT & AUTONOMIE
    # ---------------------------------------------------------
    with tab1:
        st.subheader("⚙️ Données du Site")
        col_a, col_b = st.columns(2)
        with col_a:
            i_site = st.number_input("Courant Charge Site (A)", value=25.0, step=1.0)
            v_site = st.selectbox("Tension Système (V)", [48, 24, 12], index=0)
        with col_b:
            choix_bat = st.selectbox("Modèle de Batterie", list(DICT_BATTERIES.keys()))
            h_visée = st.number_input("Autonomie visée (h)", value=24.0, step=1.0)

        # Récupération des caractéristiques du modèle choisi
        v_bat_u, ah_bat_u = DICT_BATTERIES[choix_bat]

        # --- CALCULS ---
        # 1. Nombre de batteries en série pour atteindre la tension système
        nb_serie = math.ceil(v_site / v_bat_u)

        # 2. Nombre de branches en parallèle pour l'autonomie visée (DoD 70%)
        # Capacité nécessaire = (Courant * Heures) / 0.7
        cap_necessaire = (i_site * h_visée) / 0.7
        nb_para = math.ceil(cap_necessaire / ah_bat_u)
        
        # 3. Autonomie Réelle avec ce nombre de branches
        cap_totale_installee = nb_para * ah_bat_u
        autonomie_reelle = (cap_totale_installee * 0.7) / i_site

        # 4. Solaire & GE
        i_rech = cap_totale_installee * 0.1
        i_total = i_site + i_rech
        nb_pv = math.ceil((i_total * v_site * 1.3 / 5) / 550) # Panneau 550Wc
        kva_ge = ((i_total * v_site / 800) * 1.25)

        st.divider()
        st.subheader("📋 Résultat de l'Expert")
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Branches en Parallèle", f"{nb_para}")
            st.metric("Total Unités", f"{nb_para * nb_serie} bat.")
            st.metric("Panneaux (550Wc)", f"{nb_pv} mod.")
        with m2:
            st.warning(f"**Autonomie : {autonomie_reelle:.1f} heures**")
            st.metric("Capacité Totale", f"{cap_totale_installee} Ah")
            st.metric("Groupe (GE)", f"{kva_ge:.1f} kVA")

    # ---------------------------------------------------------
    # INTERFACE 2 : CÂBLAGE & PROTECTIONS
    # ---------------------------------------------------------
    with tab2:
        st.subheader("🛡️ Sécurité Câblage")
        # On récupère le courant total calculé en tab1
        i_max_calc = i_site + (nb_para * ah_bat_u * 0.1)
        
        i_input = st.number_input("Courant Total à protéger (A)", value=float(i_max_calc), step=1.0)
        dist = st.number_input("Longueur Câble (m)", value=5.0, step=1.0)
        
        # Chute de tension max 1%
        s_chute = (2 * RHO * dist * i_input) / (v_site * 0.01)
        s_retenue = next((s for s in SECTIONS_STD if s >= s_chute and AMPACITE_CABLE[s] >= i_input), 150)
        dj_val = next((d for d in CALIBRES_DJ if d >= i_input * 1.25), "Hors Limite")

        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("Section Câble", f"{s_retenue} mm²")
        c2.metric("Disjoncteur", f"{dj_val} A")

        if isinstance(dj_val, (int, float)) and dj_val > AMPACITE_CABLE.get(s_retenue, 0):
            st.error("🔥 Risque d'incendie détecté !")
        else:
            st.success("✅ Dimensionnement sécurisé")

if __name__ == "__main__":
    main()
