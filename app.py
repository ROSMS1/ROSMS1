import streamlit as st
import math

# --- Configuration de la Page ---
st.set_page_config(
    page_title="ROSMS1 Hybrid Expert v3",
    page_icon="📡",
    layout="centered"
)

# --- Styles CSS Personnalisés (Fusion des deux styles HTML) ---
st.markdown("""
    <style>
    /* Global */
    .stApp { background-color: #f3f4f6; }
    
    /* Style Onglet 1 (Clair comme solaire.html) */
    .dim-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; color: #374151; }
    
    /* Style Onglet 2 (Sombre comme Power_dimension.html) */
    .diag-container { background-color: #0f172a; color: #f8fafc; padding: 25px; border-radius: 16px; border: 1px solid #334155; }
    .metric-card { background: #1e293b; border-radius: 12px; padding: 15px; border: 1px solid #334155; text-align: center; }
    
    /* Polices */
    html, body, [class*="css"] { font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Constantes Techniques ---
RHO = 0.0175 
DATA_CABLES = {1.5: 15, 2.5: 21, 4: 28, 6: 36, 10: 50, 16: 68, 25: 89, 35: 110, 50: 134, 70: 171, 95: 210, 120: 240, 150: 280}
SECTIONS_STD = sorted(list(DATA_CABLES.keys()))
CALIBRES_DJ = [2, 4, 6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200]

DICT_BATTERIES = {
    "2V 800Ah (OPzV)": [2, 800],
    "2V 1000Ah (Industriel)": [2, 1000],
    "12V 200Ah (Gel)": [12, 200],
    "48V 100Ah (Lithium)": [48, 100],
    "48V 200Ah (Lithium)": [48, 200]
}

def main():
    st.markdown("<h1 style='text-align: center; color: #1e40af;'>📡 ROSMS1 Hybrid Expert</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊 Dimensionnement Solaire", "🛡️ Diagnostic Câblage"])

    # ---------------------------------------------------------
    # INTERFACE 1 : DIMENSIONNEMENT (Style Solaire.html)
    # ---------------------------------------------------------
    with tab1:
        st.markdown("<div class='dim-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            i_site = st.number_input("Courant Charge Site (A)", value=25.0, step=1.0)
            v_site = st.selectbox("Tension Système (V)", [48, 24, 12], index=0)
            p_pv_u = st.number_input("Puissance Panneau Solaire (Wc)", value=550, step=10)
        with col2:
            choix_bat = st.selectbox("Modèle Batterie", list(DICT_BATTERIES.keys()))
            h_auto = st.number_input("Autonomie souhaitée (h)", value=24.0, step=1.0)
            dist_bat = st.number_input("Distance Bat - Rectifieur (m)", value=3.0, step=0.5)
        st.markdown("</div>", unsafe_allow_html=True)

        # Calculs (Logique solaire.html)
        v_bat_u, ah_bat_u = DICT_BATTERIES[choix_bat]
        p_charge = i_site * v_site
        cap_req = (p_charge * h_auto) / (v_site * 0.8)
        nb_serie = math.ceil(v_site / v_bat_u)
        nb_para = math.ceil(cap_req / ah_bat_u)
        
        # Solaire & GE
        i_rech = (nb_para * ah_bat_u) * 0.1
        i_tot_charge = i_site + i_rech
        p_sol_wc = ((p_charge * 24 / 1000) * 1.3 / 5) * 1000
        nb_pv = math.ceil(p_sol_wc / p_pv_u)
        kva_ge = ((i_tot_charge * v_site) / 800) * 1.25

        # Affichage Résultats
        st.subheader("📋 Bilan Matériel")
        res1, res2, res3 = st.columns(3)
        res1.metric("Panneaux", f"{nb_pv} modules")
        res2.metric("Total Batteries", f"{nb_para * nb_serie} unités")
        res3.metric("Groupe GE", f"{kva_ge:.1f} kVA")
        st.info(f"💡 **Note :** Couplage {nb_para} branche(s) de {nb_serie} batteries en série.")

    # ---------------------------------------------------------
    # INTERFACE 2 : CÂBLAGE & SÉCURITÉ (Style Power_dimension.html)
    # ---------------------------------------------------------
    with tab2:
        st.markdown("<div class='diag-container'>", unsafe_allow_html=True)
        
        # Entrées style Power_dimension
        v_serv = st.number_input("Tension de service (V)", value=float(v_site), step=0.1, key="v_diag")
        i_diag = st.number_input("Intensité de la charge (A)", value=float(i_tot_charge), step=0.5)
        dist_c = st.number_input("Longueur câble (mètres aller-retour)", value=float(dist_bat * 2), step=1.0)
        marge = st.slider("Marge de sécurité (%)", 0, 50, 20)
        
        i_totale_marge = i_diag * (1 + marge / 100)
        
        # Calcul Chute de tension (3% max)
        delta_u_max = v_serv * 0.03
        s_chute = (2 * RHO * dist_c * i_totale_marge) / delta_u_max
        
        # Sélection section standard
        s_retenue = next((s for s in SECTIONS_STD if s >= s_chute and DATA_CABLES[s] >= i_totale_marge), None)
        dj_val = next((d for d in CALIBRES_DJ if d > i_totale_marge), "H-L")

        # Diagnostics visuels
        if s_retenue:
            if dj_val != "H-L" and dj_val >= DATA_CABLES[s_retenue]:
                st.error(f"🔥 **ALERTE :** Disjoncteur ({dj_val}A) > Limite câble ({DATA_CABLES[s_retenue]}A). Risque de feu !")
            elif s_chute > s_retenue:
                st.warning(f"⚠️ **Chute de tension :** Distance élevée, prévoyez une section supérieure.")
            else:
                st.success("✅ Dimensionnement sécurisé conforme.")
        
        # Grille de résultats style sombre
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'><small>INTENSITÉ (+MARGE)</small><br><span style='color:#38bdf8; font-size:1.5rem; font-weight:bold;'>{i_totale_marge:.1f} A</span></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><small>SECTION CÂBLE</small><br><span style='color:#34d399; font-size:1.5rem; font-weight:bold;'>{s_retenue if s_retenue else 'Trop gros'} mm²</span></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><small>DISJONCTEUR</small><br><span style='color:#f87171; font-size:1.5rem; font-weight:bold;'>{dj_val} A</span></div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
