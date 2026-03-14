import streamlit as st
import math

# --- Configuration de la Page ---
st.set_page_config(
    page_title="ROSMS1 Hybrid Expert v3",
    page_icon="📡",
    layout="centered"
)

# --- Styles CSS pour Mobile ---
st.markdown("""
    <style>
    .main { background-color: #f3f4f6; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stExpander"] { background-color: white; border-radius: 10px; }
    .reportview-container .main .block-container { max-width: 500px; padding-top: 1rem; }
    /* Adaptation police mobile */
    html, body, [class*="css"] { font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

def calculate_hybrid_system():
    st.title("📡 ROSMS1 Hybrid Expert v3")
    
    # --- SECTION 1 : DONNÉES D'ENTRÉE ---
    with st.expander("⚙️ Données d'Entrée Site", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            i_site = st.number_input("Charge Site (A)", value=40.0, step=1.0)
            p_pv_u = st.number_input("Puissance Panneau (Wc)", value=550, step=10)
        with col2:
            v_site = st.selectbox("Tension Système (V)", [48, 24, 12], index=0)
            ah_bat_u = st.number_input("Cap. Bat. Unitaire (Ah)", value=600, step=50)
            
        h_auto = st.number_input("Autonomie souhaitée (Heures)", value=12.0, step=1.0)
        dist_bat = st.number_input("Distance Câblage (mètres)", value=5.0, step=0.5)

    # --- CONSTANTES TECHNIQUES ---
    rho = 0.0175  # Résistivité du cuivre
    sections_std = [10, 16, 25, 35, 50, 70, 95, 120, 150]
    calibres_dj = [10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250]
    # Capacité de courant max par section (approximatif pour diagnostic sécurité)
    ampacite = {10: 50, 16: 68, 25: 89, 35: 110, 50: 134, 70: 171, 95: 210, 120: 240, 150: 280}

    # --- CALCULS LOGIQUES ---
    # 1. Batteries
    # Formule : (Charge * Heures) / (Tension * Profondeur de décharge 70%)
    p_charge = i_site * v_site
    cap_totale_req = (p_charge * h_auto) / (v_site * 0.7)
    nb_para = math.ceil(cap_totale_req / ah_bat_u)
    total_bat_unites = nb_para * (v_site / 2 if ah_bat_u > 300 else 1) # Simplification pour 2V vs 12/48V

    # 2. Solaire & Recharge
    i_recharge = (nb_para * ah_bat_u) * 0.1  # Courant de charge à 10% de C10
    i_total_systeme = i_site + i_recharge
    
    # Besoin solaire (5h d'ensoleillement moyen, facteur de perte 1.3)
    p_sol_wc = ((i_total_systeme * v_site * 24 / 1000) * 1.3 / 5) * 1000
    nb_pv = math.ceil(p_sol_wc / p_pv_u)

    # 3. Groupe Électrogène (GE)
    # Calcul basé sur la puissance du rectifieur nécessaire avec marge de 25%
    kva_ge = ((i_total_systeme * v_site) / 800) * 1.25

    # 4. Câblage (Chute de tension 1% max pour les batteries)
    delta_u_max = v_site * 0.01
    s_calc = (2 * rho * dist_bat * i_total_systeme) / delta_u_max
    s_retenue = next((s for s in sections_std if s >= s_calc and s >= i_total_systeme/4), 150)

    # 5. Protection (Disjoncteur)
    dj_conseille = next((d for d in calibres_dj if d >= i_total_systeme * 1.25), "Hors Norme")

    # --- AFFICHAGE DES RÉSULTATS ---
    st.subheader("📋 Bilan du Dimensionnement")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Panneaux (Units)", f"{nb_pv} mod.")
        st.metric("Groupe Électrogène", f"{kva_ge:.1f} kVA")
    with c2:
        st.metric("Parc Batteries", f"{nb_para} branche(s)")
        st.metric("Section Câble", f"{s_retenue} mm²")

    # --- DIAGNOSTIC & SÉCURITÉ ---
    st.subheader("⚡ Sécurité & Protections")
    
    # Alerte Risque d'incendie (Si DJ > Capacité Câble)
    if isinstance(dj_conseille, int) and s_retenue in ampacite:
        if dj_conseille > ampacite[s_retenue]:
            st.error(f"🔥 ALERTE : Le disjoncteur ({dj_conseille}A) est trop élevé pour un câble de {s_retenue}mm². Risque d'incendie !")
        else:
            st.success(f"✅ Protection : Disjoncteur {dj_conseille}A recommandé.")
    
    with st.expander("🔍 Détails Techniques"):
        st.write(f"**Courant de charge batteries :** {i_recharge:.1f} A")
        st.write(f"**Courant total max (Site + Charge) :** {i_total_systeme:.1f} A")
        st.write(f"**Chute de tension calculée :** {((2 * rho * dist_bat * i_total_systeme) / s_retenue):.2f} V")

if __name__ == "__main__":
    calculate_hybrid_system()
