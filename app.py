import streamlit as st
import math

# --- Configuration de la Page ---
st.set_page_config(
    page_title="ROSMS1 Hybrid Expert v3",
    page_icon="📡",
    layout="centered"
)

# --- Design CSS pour Mobile ---
st.markdown("""
    <style>
    .stApp { background-color: #f3f4f6; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: bold; color: #1e40af; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: bold;
    }
    /* Taille de police moyenne pour smartphone */
    html, body, [class*="css"] { font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Constantes Techniques ---
RHO = 0.0175  # Résistivité du cuivre
SECTIONS_STD = [10, 16, 25, 35, 50, 70, 95, 120, 150]
CALIBRES_DJ = [10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200]
AMPACITE_CABLE = {10: 50, 16: 68, 25: 89, 35: 110, 50: 134, 70: 171, 95: 210, 120: 240, 150: 280}

def main():
    st.title("📡 ROSMS1 Hybrid Expert v3")

    # --- Les deux interfaces via des Onglets ---
    tab1, tab2 = st.tabs(["📊 Dimensionnement", "⚡ Câblage & Protections"])

    # ---------------------------------------------------------
    # INTERFACE 1 : DIMENSIONNEMENT
    # ---------------------------------------------------------
    with tab1:
        with st.container():
            st.subheader("⚙️ Données d'Entrée Site")
            col1, col2 = st.columns(2)
            with col1:
                i_site = st.number_input("Charge Site (A)", value=40.0, step=1.0, key="dim_i")
                p_pv_u = st.number_input("Puissance Panneau (Wc)", value=450, step=10)
            with col2:
                v_site = st.number_input("Tension (V)", value=48, disabled=True)
                ah_bat_u = st.number_input("Bat. Unitaire (Ah)", value=600, step=50)
            
            h_auto = st.number_input("Autonomie souhaitée (Heures)", value=12.0, step=1.0)

        # Calculs Logiques
        # 1. Batteries (70% DoD)
        nb_para = math.ceil((i_site * h_auto / 0.7) / ah_bat_u)
        
        # 2. Solaire & GE
        i_rech = nb_para * ah_bat_u * 0.1
        i_tot_systeme = i_site + i_rech
        # Facteur 1.25 pour pertes et 4.5h d'ensoleillement
        nb_pv = math.ceil((i_tot_systeme * v_site * 1.25 / 4.5) / p_pv_u)
        kva_ge = ((i_tot_systeme * v_site / 800) * 1.3)

        # Section de câble recommandée pour la dimension (Courant total / densité 3.5 A/mm²)
        s_dim = next((s for s in SECTIONS_STD if s >= i_tot_systeme / 3.5), 150)

        st.divider()
        st.subheader("📋 Bilan Matériel")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Panneaux", f"{nb_pv} mod.")
            st.metric("Batteries (48V)", f"{nb_para} branche(s)")
        with c2:
            st.metric("Groupe (GE)", f"{kva_ge:.1f} kVA")
            st.metric("Câble Bat.", f"{s_dim} mm²")

    # ---------------------------------------------------------
    # INTERFACE 2 : CÂBLAGE & PROTECTIONS
    # ---------------------------------------------------------
    with tab2:
        with st.container():
            st.subheader("🛡️ Calcul de Sécurité")
            i_total_prot = st.number_input("Courant Total (A)", value=60.0, step=1.0, key="prot_i")
            l_cable = st.number_input("Longueur Câble (m)", value=5.0, step=0.5)
            
        # Calcul Chute de Tension (Max 1% sur 48V)
        s_chute = (2 * RHO * l_cable * i_total_prot) / (48 * 0.01)
        
        # Sélection Section (Doit respecter la chute de tension ET l'ampacité thermique)
        s_retenue = next((s for s in SECTIONS_STD if s >= s_chute and AMPACITE_CABLE[s] >= i_total_prot), 150)
        
        # Sélection Disjoncteur (125% du courant nominal)
        dj_val = next((d for d in CALIBRES_DJ if d >= i_total_prot * 1.25), "H-L")

        st.divider()
        res1, res2 = st.columns(2)
        with res1:
            st.metric("Section Requise", f"{s_retenue} mm²")
        with res2:
            st.metric("Disjoncteur", f"{dj_val} A")

        # Diagnostic de sécurité
        if isinstance(dj_val, int) and dj_val > AMPACITE_CABLE.get(s_retenue, 0):
            st.error(f"🔥 Risque d'incendie : Le disjoncteur ({dj_val}A) est trop fort pour un câble de {s_retenue}mm².")
        else:
            st.success("✅ Protection conforme aux normes de sécurité.")

if __name__ == "__main__":
    main()
