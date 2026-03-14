import streamlit as st
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(page_title="ROSMS1 Expert", layout="centered")

# On définit le code HTML amélioré ici
html_code = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f3f4f6; font-family: sans-serif; font-size: 0.85rem; }
        .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 3px; color: #4b5563; font-size: 0.75rem; }
        input, select { width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; margin-bottom: 10px; font-size: 0.8rem; }
        .result-val { font-size: 1.1rem; font-weight: bold; color: #1e40af; }
        .tab-btn { padding: 10px; width: 50%; font-weight: bold; cursor: pointer; border-bottom: 2px solid transparent; text-align: center; }
        .tab-active { border-bottom: 2px solid #1e40af; color: #1e40af; background-color: #eff6ff; }
    </style>
</head>
<body class="p-2">
    <h1 class="text-xl font-bold text-center text-blue-900 mb-4">🚀 ROSMS1 Hybrid Expert v3</h1>
    
    <div class="flex mb-4 bg-white rounded-lg shadow-sm overflow-hidden">
        <div id="tab1" class="tab-btn tab-active" onclick="switchTab(1)">Dimensionnement</div>
        <div id="tab2" class="tab-btn" onclick="switchTab(2)">Câblage & Protections</div>
    </div>

    <div id="content1">
        <div class="card">
            <h2 class="text-sm font-bold text-blue-700 mb-3 border-b pb-1">⚙️ Données d'Entrée Site</h2>
            <div class="grid grid-cols-2 gap-3">
                <div><label>Charge Site (A)</label><input type="number" id="i_site" value="40" oninput="calculerGlobal()"></div>
                <div><label>Tension (V)</label><input type="number" id="v_site" value="48" readonly class="bg-gray-100"></div>
                <div><label>Panneau (Wc)</label><input type="number" id="p_pv_u" value="450" oninput="calculerGlobal()"></div>
                <div><label>Bat. Unitaire (Ah)</label><input type="number" id="ah_bat_u" value="600" oninput="calculerGlobal()"></div>
            </div>
            <label>Autonomie souhaitée (Heures)</label>
            <input type="number" id="h_auto" value="12" oninput="calculerGlobal()">
        </div>

        <div class="card border-l-4 border-blue-600 bg-blue-50">
            <h2 class="text-sm font-bold text-blue-800 mb-3">📋 Bilan Matériel</h2>
            <div class="grid grid-cols-2 gap-4">
                <div class="bg-white p-2 rounded shadow-sm"><p class="text-[0.65rem] text-gray-500">Panneaux</p><p id="res_pv" class="result-val">0 mod.</p></div>
                <div class="bg-white p-2 rounded shadow-sm"><p class="text-[0.65rem] text-gray-500">Batteries</p><p id="res_bat" class="result-val">0 unités</p></div>
                <div class="bg-white p-2 rounded shadow-sm"><p class="text-[0.65rem] text-gray-500">Groupe (GE)</p><p id="res_ge" class="result-val">0 kVA</p></div>
                <div class="bg-white p-2 rounded shadow-sm"><p class="text-[0.65rem] text-gray-500">Câble Bat.</p><p id="res_cable_dim" class="result-val text-red-600">0 mm²</p></div>
            </div>
        </div>
    </div>

    <div id="content2" class="hidden">
        <div class="card">
            <h2 class="text-sm font-bold text-green-700 mb-3 border-b pb-1">⚡ Protections</h2>
            <label>Courant Total (A)</label><input type="number" id="i_total_prot" value="60" oninput="calculerProtection()">
            <label>Longueur Câble (m)</label><input type="number" id="l_cable" value="5" oninput="calculerProtection()">
        </div>
        <div class="card border-l-4 border-green-600 bg-green-50">
            <div class="space-y-4">
                <div class="flex justify-between items-center bg-white p-3 rounded shadow-sm"><span class="text-xs">Section :</span><span id="prot_section" class="text-lg font-bold">0 mm²</span></div>
                <div class="flex justify-between items-center bg-white p-3 rounded shadow-sm"><span class="text-xs">Disjoncteur :</span><span id="prot_dj" class="text-lg font-bold text-red-600">0 A</span></div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(t) {
            document.getElementById('content1').classList.toggle('hidden', t!==1);
            document.getElementById('content2').classList.toggle('hidden', t!==2);
            document.getElementById('tab1').classList.toggle('tab-active', t===1);
            document.getElementById('tab2').classList.toggle('tab-active', t===2);
        }
        function calculerGlobal() {
            const i=parseFloat(document.getElementById('i_site').value)||0, p=parseFloat(document.getElementById('p_pv_u').value)||450;
            const ah=parseFloat(document.getElementById('ah_bat_u').value)||600, h=parseFloat(document.getElementById('h_auto').value)||0;
            const nb_para=Math.ceil((i*h/0.7)/ah), i_rech=nb_para*ah*0.1, i_tot=i+i_rech;
            document.getElementById('res_pv').innerText=Math.ceil((i_tot*48*1.2/4.5)/p)+" mod.";
            document.getElementById('res_bat').innerText=nb_para+" (48V)";
            document.getElementById('res_ge').innerText=((i_tot*48/800)*1.3).toFixed(1)+" kVA";
            document.getElementById('res_cable_dim').innerText=([16,25,35,50,70,95,120].find(s=>s>=i_tot/3.5)||150)+" mm²";
        }
        function calculerProtection() {
            const i=parseFloat(document.getElementById('i_total_prot').value)||0, d=parseFloat(document.getElementById('l_cable').value)||0;
            const s_ch= (2*0.0175*d*i)/(48*0.01);
            document.getElementById('prot_section').innerText=([10,16,25,35,50,70,95,120].find(s=>s>=s_ch && s>=i/4)||150)+" mm²";
            document.getElementById('prot_dj').innerText=([10,16,20,25,32,40,50,63,80,100,125,160,200].find(d=>d>=i*1.25)||"+200")+" A";
        }
        window.onload=()=>{calculerGlobal();calculerProtection();};
    </script>
</body>
</html>
"""

# Injection du code HTML dans l'interface Streamlit
components.html(html_code, height=800, scrolling=True)
