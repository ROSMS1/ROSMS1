import streamlit as st
import math

# --- Configuration de la Page ---
st.set_page_config(
    page_title="ROSMS1 Hybrid Expert v3",
    page_icon="📡",
    layout="centered"
)

# --- Style CSS optimisé pour mobile ---
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
    /* Police moyenne pour lisibilité sur smartphone */
    html, body, [class*="css"] { font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Constantes Techniques ---
RHO = 0.0175 
SECTIONS_STD = [10, 16, 25, 35, 50, 70, 95, 120, 150]
CALIBRES_DJ = [10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200]
AMPACITE_CABLE = {10: 50, 16: 68, 25: 89, 35: 110, 50: 134, 70: 171, 95: 210, 120: 240, 150: 280}

def main():
    st.title("📡 ROSMS1 Hybrid Expert")

    tab1, tab2 = st.tabs(["📊 Dimensionnement", "⚡ Câblage & Sécurité"])

    # ---------------------------------------------------------
    # INTERFACE 1 : DIMENSIONNEMENT ET RECOMMANDATIONS
    # ---------------------------------------------------------
    with tab1:
        st.subheader("⚙️ Paramètres de Charge")
        col_a, col_b = st.columns(2)
        with col_a:
            i_site = st.number_input("Courant Charge Site (A)", value=25.0, step=1.0)
            v_site = st.selectbox("Tension Système (V)", [48, 24, 12], index=0)
        with col_b:
            ah_bat_u = st.number_input("Capacité Bat. (Ah)", value=200, step=50)
            h_souhaite = st.number_input("Autonomie visée (h)", value=24.0, step=1.0)

        # --- LOGIQUE DE RECOMMANDATION BATTERIE ---
        # 1. Calcul de la capacité totale nécessaire (70% de décharge max pour préserver la durée de vie)
        cap_totale_necessaire = (i_site * h_souhaite) / 0.7
        
        # 2. Nombre de branches en parallèle recommandées
        nb_para_rec = math.ceil(cap_totale_necessaire / ah_bat_u)
        
        # 3. Nombre total d'unités (Si batterie 12V sur un système 48V, il faut 4 en série)
        v_bat_u = 12 if ah_bat_u <= 250 else 2 # Hypothèse : Monobloc 12V ou Élément 2V
        nb_serie = math.ceil(v_site / v_bat_u)
        total_unites = nb_para_rec * nb_serie

        # --- CALCUL DE L'AUTONOMIE RÉELLE ---
        # Autonomie = (Capacité totale * Tension * 0.7) / Puissance de charge
        cap_installée = nb_para_rec * ah_bat_u
        autonomie_reelle = (cap_installée * 0.7) / i_site

        # --- CALCUL SOLAIRE & GE ---
        i_rech = cap_installée * 0.1 # Courant recharge 10% de C10
        i_total = i_site + i_rech
        nb_pv = math.ceil((i_total * v_site * 1.3 / 5) / 550) # Base panneau 550Wc
        kva_ge = ((i_total * v_site / 800) * 1.25)

        st.divider()
        st.subheader("📋 Recommandations")
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Batteries à installer", f"{nb_para_rec} branche(s)", help=f"Soit {total_unites} unités au total")
            st.metric("Panneaux (550Wc)", f"{nb_pv} modules")
        with m2:
            st.metric("Autonomie Réelle", f"{autonomie_reelle:.1f} heures")
            st.metric("Groupe (GE)", f"{kva_ge:.1f} kVA")

    # ---------------------------------------------------------
    # INTERFACE 2 : CÂBLAGE & PROTECTIONS
    # ---------------------------------------------------------
    with tab2:
        st.subheader("🛡️ Calcul de Section et Protection")
        i_max = st.number_input("Courant Total (A)", value=float(i_total), step=1.0)
        dist = st.number_input("Longueur Câble (m)", value=5.0, step=1.0)
        
        # Chute de tension max 1%
        s_chute = (2 * RHO * dist * i_max) / (v_site * 0.01)
        s_retenue = next((s for s in SECTIONS_STD if s >= s_chute and AMPACITE_CABLE[s] >= i_max), 150)
        dj_val = next((d for d in CALIBRES_DJ if d >= i_max * 1.25), "H-L")

        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("Section Câble", f"{s_retenue} mm²")
        c2.metric("Disjoncteur", f"{dj_val} A")

        if isinstance(dj_val, int) and dj_val > AMPACITE_CABLE.get(s_retenue, 0):
            st.error("🔥 Attention : Risque thermique (DJ > Capacité Câble)")
        else:
            st.success("✅ Installation sécurisée")

if __name__ == "__main__":
    main()
