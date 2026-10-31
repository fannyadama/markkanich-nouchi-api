<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markkanich Nouchi - Dictionnaire de l'argot ivoirien</title>
    <meta name="description" content="Le dictionnaire complet du Nouchi, l'argot ivoirien. 263+ mots avec prononciations et exemples.">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f4f4f9; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; }
        header { text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); color: white; border-radius: 12px; margin-bottom: 30px; }
        h1 { font-size: 2.2em; margin-bottom: 10px; }
        .user-bar { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .user-info { font-size: 0.9em; }
        .plan-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85em; }
        .plan-gratuit { background: #e0e0e0; color: #555; }
        .plan-premium { background: #ffd700; color: #333; }
        .plan-pro { background: #4a90e2; color: white; }
        .search-box { display: flex; gap: 10px; margin-bottom: 20px; }
        input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; }
        input:focus { outline: none; border-color: #ff6b35; }
        button { padding: 12px 20px; background: #ff6b35; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        button:hover { background: #e55a2b; }
        .mot-card { background: white; padding: 20px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 5px solid #ff6b35; }
        .mot-card.premium { border-left-color: #ffd700; position: relative; }
        .premium-lock { position: absolute; top: 10px; right: 10px; background: #ffd700; color: #333; padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: bold; }
        .mot-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 10px; }
        .mot-header h3 { color: #2c3e50; }
        .prononciation { color: #888; font-style: italic; margin-bottom: 8px; }
        .categorie { background: #fff3e0; color: #ff6b35; padding: 4px 10px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
        .exemple { background: #f8f9fa; padding: 10px; border-radius: 6px; font-style: italic; color: #555; margin-top: 10px; border-left: 3px solid #ff6b35; }
        .plans-section, .contrib-section { background: white; padding: 30px; border-radius: 12px; margin: 30px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        .plans-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .plan-card { border: 2px solid #e0e0e0; border-radius: 12px; padding: 25px; text-align: center; transition: all 0.3s; }
        .plan-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
        .plan-card.featured { border-color: #ffd700; background: linear-gradient(135deg, #fff9e6 0%, #fff 100%); }
        .plan-card h3 { font-size: 1.5em; margin-bottom: 10px; }
        .plan-price { font-size: 2em; font-weight: bold; color: #ff6b35; margin: 15px 0; }
        .plan-price small { font-size: 0.5em; color: #888; }
        .plan-features { list-style: none; text-align: left; margin: 20px 0; }
        .plan-features li { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
        .plan-features li:before { content: "✓ "; color: #28a745; font-weight: bold; }
        .btn-pay { width: 100%; padding: 14px; background: #ff6b35; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 1em; }
        .btn-pay:hover { background: #e55a2b; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 1000; justify-content: center; align-items: center; }
        .modal.active { display: flex; }
        .modal-content { background: white; padding: 30px; border-radius: 12px; max-width: 500px; width: 90%; }
        .modal-content h2 { color: #ff6b35; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; }
        .loading { text-align: center; padding: 20px; color: #666; }
        #stats { text-align: center; margin-bottom: 20px; font-weight: bold; background: white; padding: 15px; border-radius: 8px; }
        footer { text-align: center; margin-top: 40px; padding: 20px; color: #666; }
    </style>
</head>
<body>
    <header>
        <h1>🇨🇮 Markkanich Nouchi</h1>
        <p>Le dictionnaire de l'argot ivoirien</p>
    </header>

    <div class="user-bar">
        <div class="user-info" id="userInfo">👤 Visiteur - <a href="#" onclick="ouvrirModalConnexion()" style="color:#ff6b35">Se connecter</a></div>
        <div id="planBadge"></div>
    </div>

    <div id="stats">Chargement...</div>

    <div class="search-box">
        <input type="text" id="searchInput" placeholder="Rechercher un mot (ex: goumin, enjailler...)">
        <button onclick="chercher()">🔍 Rechercher</button>
    </div>

    <div id="results"></div>

    <div class="plans-section">
        <h2 style="text-align:center; color:#2c3e50">💎 Choisissez votre plan</h2>
        <p style="text-align:center; color:#666; margin-top:10px">Accédez à tous les mots nouchi et fonctionnalités avancées</p>
        <div class="plans-grid">
            <div class="plan-card">
                <h3>🆓 Gratuit</h3>
                <div class="plan-price">0 <small>FCFA</small></div>
                <ul class="plan-features">
                    <li>20 mots essentiels</li>
                    <li>5 recherches/jour</li>
                    <li>Définitions de base</li>
                </ul>
                <button class="btn-pay" onclick="ouvrirModalConnexion()">Commencer</button>
            </div>
            <div class="plan-card featured">
                <h3>⭐ Premium</h3>
                <div class="plan-price">2 500 <small>FCFA/mois</small></div>
                <ul class="plan-features">
                    <li>263+ mots complets</li>
                    <li>Recherches illimitées</li>
                    <li>Prononciations audio</li>
                    <li>Quiz d'apprentissage</li>
                </ul>
                <button class="btn-pay" onclick="initierPaiement('premium')">Devenir Premium</button>
            </div>
            <div class="plan-card">
                <h3>💼 Pro / API</h3>
                <div class="plan-price">15 000 <small>FCFA/mois</small></div>
                <ul class="plan-features">
                    <li>Tout le Premium</li>
                    <li>Accès API complet</li>
                    <li>Usage commercial</li>
                    <li>Support prioritaire</li>
                </ul>
                <button class="btn-pay" onclick="initierPaiement('pro')">Choisir Pro</button>
            </div>
        </div>
    </div>

    <!-- FORMULAIRE DE CONTRIBUTION -->
    <div class="contrib-section">
        <h2 style="text-align:center; color:#2c3e50; margin-bottom: 10px;">💡 Proposer un mot Nouchi</h2>
        <p style="text-align:center; color:#666; margin-bottom: 25px; font-size: 0.9em;">Tu connais un mot qui manque ? Soumets-le à nos experts pour validation !</p>
        <div style="display: flex; flex-direction: column; gap: 15px; max-width: 500px; margin: 0 auto;">
            <div>
                <label style="font-weight: bold; font-size: 0.9em; color: #333;">Mot en Nouchi *</label>
                <input type="text" id="propMot" placeholder="Ex: Enjailler" style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; margin-top: 5px;">
            </div>
            <div>
                <label style="font-weight: bold; font-size: 0.9em; color: #333;">Définition *</label>
                <input type="text" id="propDef" placeholder="Ex: Séduire, charmer" style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; margin-top: 5px;">
            </div>
            <div>
                <label style="font-weight: bold; font-size: 0.9em; color: #333;">Exemple (optionnel)</label>
                <input type="text" id="propEx" placeholder="Ex: Il a réussi à l'enjailler" style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; margin-top: 5px;">
            </div>
            <div>
                <label style="font-weight: bold; font-size: 0.9em; color: #333;">Ton email</label>
                <input type="email" id="propEmail" placeholder="ton@email.com" style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; margin-top: 5px;">
            </div>
            <button onclick="soumettreProposition()" style="width: 100%; padding: 14px; background: #28a745; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 1.1em; margin-top: 10px;">📤 Soumettre pour validation</button>
            <p id="propMessage" style="text-align: center; margin-top: 10px; font-weight: bold;"></p>
        </div>
    </div>

    <!-- Modal de connexion -->
    <div class="modal" id="modalConnexion">
        <div class="modal-content">
            <h2>🔐 Connexion</h2>
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="emailInput" placeholder="ton@email.com">
            </div>
            <button class="btn-pay" onclick="seConnecter()">Se connecter</button>
            <button onclick="fermerModal()" style="margin-top:10px; background:#ccc; width:100%">Annuler</button>
        </div>
    </div>

    <footer>
        <p>© 2026 Mark Kanich | Dictionnaire Nouchi - Tous droits réservés</p>
    </footer>

    <script src="https://js.paystack.co/v1/inline.js"></script>
    <script>
        const API_URL = "https://markkanich-nouchi-api.onrender.com";
        let utilisateurActuel = null;

        window.onload = function() {
            const email = localStorage.getItem("email");
            if (email) verifierUtilisateur(email);
            chargerStats();
            chargerMotsGratuits();
        };

        async function chargerStats() {
            try {
                const stats = await fetch(API_URL + "/stats").then(r => r.json());
                document.getElementById("stats").innerText = `📚 ${stats.total_mots} mots | 🏷️ ${stats.total_categories} catégories`;
            } catch(e) { console.error(e); }
        }

        async function chargerMotsGratuits() {
            document.getElementById("results").innerHTML = '<div class="loading">Chargement...</div>';
            try {
                const mots = await fetch(API_URL + "/mots/gratuits").then(r => r.json());
                afficherMots(mots, false);
            } catch(e) {
                document.getElementById("results").innerHTML = '<div class="loading">Erreur de chargement</div>';
            }
        }

        async function chargerMotsComplets(q = "") {
            if (!utilisateurActuel || utilisateurActuel.plan === "gratuit") {
                ouvrirModalConnexion();
                alert("Passez au plan Premium pour accéder à tous les mots !");
                return;
            }
            document.getElementById("results").innerHTML = '<div class="loading">Chargement...</div>';
            try {
                const url = q ? `${API_URL}/mots/complet?email=${utilisateurActuel.email}&q=${q}` : `${API_URL}/mots/complet?email=${utilisateurActuel.email}&limite=50`;
                const mots = await fetch(url).then(r => r.json());
                afficherMots(mots, true);
            } catch(e) {
                document.getElementById("results").innerHTML = '<div class="loading">Erreur. Vérifiez votre abonnement.</div>';
            }
        }

        function afficherMots(mots, isPremium) {
            if (mots.length === 0) {
                document.getElementById("results").innerHTML = '<div class="loading">Aucun mot trouvé.</div>';
                return;
            }
            document.getElementById("results").innerHTML = mots.map(m => `
                <div class="mot-card ${m.is_premium ? 'premium' : ''}">
                    ${m.is_premium ? '<span class="premium-lock">⭐ PREMIUM</span>' : ''}
                    <div class="mot-header">
                        <h3>${m.mot}</h3>
                        <span class="categorie">${m.categorie || 'Général'}</span>
                    </div>
                    <div class="prononciation">${m.prononciation || ''}</div>
                    <p><strong>Définition :</strong> ${m.definition}</p>
                    ${m.exemple ? `<div class="exemple">« ${m.exemple} »</div>` : ''}
                </div>
            `).join('');
        }

        function chercher() {
            const q = document.getElementById("searchInput").value;
            if (utilisateurActuel && utilisateurActuel.plan !== "gratuit") {
                chargerMotsComplets(q);
            } else {
                chargerMotsGratuits(); // Pour la recherche, on pourrait aussi limiter aux gratuits si pas connecté
            }
        }

        document.getElementById("searchInput").addEventListener("keypress", function(e) {
            if (e.key === "Enter") chercher();
        });

        function ouvrirModalConnexion() { document.getElementById("modalConnexion").classList.add("active"); }
        function fermerModal() { document.getElementById("modalConnexion").classList.remove("active"); }

        async function seConnecter() {
            const email = document.getElementById("emailInput").value;
            if (!email) { alert("Entrez votre email"); return; }
            try {
                const res = await fetch(API_URL + "/connexion", {
                    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({email: email})
                });
                const data = await res.json();
                utilisateurActuel = data;
                localStorage.setItem("email", email);
                mettreAJourUI();
                fermerModal();
                if (data.plan !== "gratuit") chargerMotsComplets();
            } catch(e) { alert("Erreur de connexion"); }
        }

        function mettreAJourUI() {
            if (!utilisateurActuel) return;
            document.getElementById("userInfo").innerHTML = `👤 ${utilisateurActuel.email}`;
            const planClass = `plan-${utilisateurActuel.plan}`;
            const planLabel = utilisateurActuel.plan.charAt(0).toUpperCase() + utilisateurActuel.plan.slice(1);
            document.getElementById("planBadge").innerHTML = `<span class="plan-badge ${planClass}">${planLabel}</span>`;
        }

        async function initierPaiement(plan) {
            const email = localStorage.getItem("email");
            if (!email) { ouvrirModalConnexion(); alert("Connectez-vous d'abord pour payer"); return; }
            try {
                const res = await fetch(API_URL + "/initier-paiement", {
                    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({email: email, plan: plan})
                });
                const data = await res.json();
                if (data.status === "success") {
                    const handler = PaystackPop.setup({
                        key: 'pk_test_VOTRE_CLE_PUBLIQUE_PAYSTACK', // ⚠️ REMPLACE CECI PAR TA VRAIE CLÉ PUBLIQUE (commence par pk_test_)
                        email: email,
                        amount: plan === "premium" ? 250000 : 1500000,
                        currency: 'XOF',
                        ref: data.reference,
                        metadata: {plan: plan},
                        callback: async function(response) {
                            const verif = await fetch(API_URL + "/verifier-paiement", {
                                method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({reference: response.reference})
                            });
                            const resultat = await verif.json();
                            if (resultat.status === "success") {
                                alert("🎉 Paiement réussi ! Abonnement activé pour 30 jours.");
                                verifierUtilisateur(email);
                                chargerMotsComplets();
                            }
                        },
                        onClose: function() { alert('Paiement annulé'); }
                    });
                    handler.openIframe();
                }
            } catch(e) { alert("Erreur lors de l'initialisation du paiement"); }
        }

        async function verifierUtilisateur(email) {
            try {
                const res = await fetch(API_URL + "/connexion", {
                    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({email: email})
                });
                utilisateurActuel = await res.json();
                mettreAJourUI();
            } catch(e) { console.error(e); }
        }

        // ==========================================
        // NOUVELLE FONCTION DE CONTRIBUTION
        // ==========================================
        async function soumettreProposition() {
            const mot = document.getElementById("propMot").value.trim();
            const def = document.getElementById("propDef").value.trim();
            const ex = document.getElementById("propEx").value.trim();
            const email = document.getElementById("propEmail").value.trim();
            const msgBox = document.getElementById("propMessage");

            if (!mot || !def) {
                msgBox.style.color = "red";
                msgBox.innerText = "⚠️ Veuillez remplir au moins le mot et la définition.";
                return;
            }

            msgBox.style.color = "#666";
            msgBox.innerText = "⏳ Envoi en cours...";

            try {
                const res = await fetch(API_URL + "/contribuer", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        mot_propose: mot,
                        definition_proposee: def,
                        exemple: ex || null,
                        email_auteur: email || null
                    })
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    msgBox.style.color = "green";
                    msgBox.innerText = "✅ " + data.message;
                    document.getElementById("propMot").value = "";
                    document.getElementById("propDef").value = "";
                    document.getElementById("propEx").value = "";
                    document.getElementById("propEmail").value = "";
                } else {
                    msgBox.style.color = "red";
                    msgBox.innerText = "⚠️ " + (data.detail || "Une erreur est survenue.");
                }
            } catch (e) {
                msgBox.style.color = "red";
                msgBox.innerText = "❌ Erreur de connexion. Réessayez plus tard.";
            }
        }
    </script>
</body>
</html>
