<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expert Telecom Hybrid Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f3f4f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 0.85rem; }
        .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 3px; color: #4b5563; font-size: 0.75rem; }
        input, select { width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; margin-bottom: 10px; font-size: 0.8rem; background-color: #f9fafb; }
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
                <div>
                    <label>Charge Site (Ampères)</label>
                    <input type="number" id="i_site" value="40" oninput="calculerGlobal()">
                </div>
                <div>
                    <label>Tension Syst. (V)</label>
                    <input type="number" id="v_site" value="48" readonly class="bg-gray-100">
                </div>
                <div>
                    <label>Puissance Panneau (Wc)</label>
                    <input type="number" id="p_pv_u" value="450" oninput="calculerGlobal()">
                </div>
                <div>
                    <label>Capacité Bat. (Ah)</label>
                    <input type="number" id="ah_bat_u" value="600" oninput="calculerGlobal()">
                </div>
            </div>
            <label>Autonomie souhaitée (Heures)</label>
            <input type="number" id="h_auto" value="12" oninput="calculerGlobal()">
        </div>

        <div class="card border-l-4 border-blue-600 bg-blue-50">
            <h2 class="text-sm font-bold text-blue-800 mb-3">📋 Bilan Matériel Recommandé</h2>
            <div class="grid grid-cols-2 gap-4">
                <div class="bg-white p-2 rounded shadow-sm">
                    <p class="text-[0.65rem] uppercase text-gray-500">Panneaux à installer</p>
                    <p id="res_pv" class="result-val">0 mod.</p>
                </div>
                <div class="bg-white p-2 rounded shadow-sm">
                    <p class="text-[0.65rem] uppercase text-gray-500">Nombre de Batteries</p>
                    <p id="res_bat" class="result-val">0 unités</p>
                </div>
                <div class="bg-white p-2 rounded shadow-sm">
                    <p class="text-[0.65rem] uppercase text-gray-500">Groupe Électrogène</p>
                    <p id="res_ge" class="result-val">0 kVA</p>
                </div>
                <div class="bg-white p-2 rounded shadow-sm">
                    <p class="text-[0.65rem] uppercase text-gray-500">Câble Batteries</p>
                    <p id="res_cable_dim" class="result-val text-red-600">0 mm²</p>
                </div>
            </div>
            <div id="res_auto" class="mt-3 text-xs font-medium text-green-700"></div>
        </div>
    </div>

    <div id="content2" class="hidden">
        <div class="card">
            <h2 class="text-sm font-bold text-green-700 mb-3 border-b pb-1">⚡ Calcul des Protections</h2>
            <label>Courant Total (Charge + Recharge)</label>
            <input type="number" id="i_total_prot" value="60" oninput="calculerProtection()">
            
            <label>Longueur de Câble (mètres)</label>
            <input type="number" id="l_cable" value="5" oninput="calculerProtection()">
        </div>

        <div class="card border-l-4 border-green-600 bg-green-50">
            <h2 class="text-sm font-bold text-green-800 mb-3">🛡️ Recommendations Câblage</h2>
            <div class="space-y-4">
                <div class="flex justify-between items-center bg-white p-3 rounded shadow-sm">
                    <span class="text-xs text-gray-600">Section de Câble :</span>
                    <span id="prot_section" class="text-lg font-bold text-green-700">0 mm²</span>
                </div>
                <div class="flex justify-between items-center bg-white p-3 rounded shadow-sm">
                    <span class="text-xs text-gray-600">Disjoncteur (DJ) :</span>
                    <span id="prot_dj" class="text-lg font-bold text-red-600">0 A</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabIndex) {
            document.getElementById('content1').classList.toggle('hidden', tabIndex !== 1);
            document.getElementById('content2').classList.toggle('hidden', tabIndex !== 2);
            document.getElementById('tab1').classList.toggle('tab-active', tabIndex === 1);
            document.getElementById('tab2').classList.toggle('tab-active', tabIndex === 2);
        }

        function calculerGlobal() {
            const i_site = parseFloat(document.getElementById('i_site').value) || 0;
            const v_site = 48;
            const p_pv_u = parseFloat(document.getElementById('p_pv_u').value) || 450;
            const ah_bat_u = parseFloat(document.getElementById('ah_bat_u').value) || 200;
            const h_auto = parseFloat(document.getElementById('h_auto').value) || 0;

            // 1. Calcul Batteries (Basé sur 70% décharge utile pour telecom)
            const cap_totale_requise = (i_site * h_auto) / 0.7;
            const nb_para = Math.ceil(cap_totale_requise / ah_bat_u);
            const nb_serie = 1; // Dans votre cas 48V est standard
            const total_bat = nb_para; 

            // 2. Calcul Solaire (Compensation 24h + recharge batterie 10%)
            const i_recharge = (nb_para * ah_bat_u) * 0.1;
            const i_total_sys = i_site + i_recharge;
            const p_solaire_wc = (i_total_sys * v_site) * 1.2 / 4.5; // Facteur correction & 4.5h soleil
            const nb_pv = Math.ceil(p_solaire_wc / p_pv_u);

            // 3. Groupe Électrogène
            const p_kva = ((i_total_sys * v_site) / 800) * 1.3;

            // 4. Section Câble (Approximation rapide densité 4A/mm2)
            const s_bat = [16, 25, 35, 50, 70, 95, 120].find(s => s >= i_total_sys / 3.5) || 150;

            // Affichage
            document.getElementById('res_pv').innerText = nb_pv + " mod.";
            document.getElementById('res_bat').innerText = total_bat + " (48V)";
            document.getElementById('res_ge').innerText = p_kva.toFixed(1) + " kVA";
            document.getElementById('res_cable_dim').innerText = s_bat + " mm²";
            document.getElementById('res_auto').innerText = "💡 Autonomie réelle : " + ((ah_bat_u * nb_para * 0.7) / i_site).toFixed(1) + " heures";
        }

        function calculerProtection() {
            const i_tot = parseFloat(document.getElementById('i_total_prot').value) || 0;
            const dist = parseFloat(document.getElementById('l_cable').value) || 0;
            const rho = 0.0175;

            // Section Chute de tension 1%
            const s_chute = (2 * rho * dist * i_tot) / (48 * 0.01);
            const s_std = [6, 10, 16, 25, 35, 50, 70, 95, 120].find(s => s >= s_chute && s >= i_tot/4) || "Speciale";
            
            // Disjoncteur
            const djs = [10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200];
            const dj_final = djs.find(d => d >= i_tot * 1.25) || "+200";

            document.getElementById('prot_section').innerText = s_std + " mm²";
            document.getElementById('prot_dj').innerText = dj_final + " A";
        }

        window.onload = () => { calculerGlobal(); calculerProtection(); };
    </script>
</body>
</html>
