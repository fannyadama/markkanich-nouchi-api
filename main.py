import json
import os
import requests
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, or_
from typing import Optional
from pydantic import BaseModel
from database import get_db, engine, Base

# ==========================================
# CONFIGURATION PAYSTACK
# ==========================================
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "")
PAYSTACK_URL = "https://api.paystack.co"

# ==========================================
# MODÈLES DE BASE DE DONNÉES
# ==========================================
class MotNouchi(Base):
    __tablename__ = "mots_nouchi"
    id = Column(Integer, primary_key=True, index=True)
    mot = Column(String, unique=True, index=True, nullable=False)
    prononciation = Column(String)
    definition = Column(Text)
    exemple = Column(Text)
    origine = Column(String)
    categorie = Column(String, index=True)
    is_premium = Column(Boolean, default=False)

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nom = Column(String)
    plan = Column(String, default="gratuit")
    date_inscription = Column(DateTime, default=datetime.utcnow)
    date_expiration = Column(DateTime)
    paystack_customer_code = Column(String)
    actif = Column(Boolean, default=True)

class Paiement(Base):
    __tablename__ = "paiements"
    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, index=True)
    reference = Column(String, unique=True, nullable=False)
    montant = Column(Integer)
    plan = Column(String)
    statut = Column(String, default="en_attente")
    date_paiement = Column(DateTime, default=datetime.utcnow)

class Proposition(Base):
    __tablename__ = "propositions"
    id = Column(Integer, primary_key=True, index=True)
    mot_propose = Column(String, nullable=False)
    definition_proposee = Column(Text, nullable=False)
    exemple = Column(Text)
    categorie = Column(String)
    email_auteur = Column(String)
    statut = Column(String, default="en_attente")
    date_proposition = Column(DateTime, default=datetime.utcnow)

# ==========================================
# SCHÉMAS PYDANTIC (Validation)
# ==========================================
class InitPaiement(BaseModel):
    email: str
    plan: str
    nom: Optional[str] = None

class VerificationPaiement(BaseModel):
    reference: str

class ConnexionUser(BaseModel):
    email: str

class ContributionIn(BaseModel):
    mot_propose: str
    definition_proposee: str
    exemple: Optional[str] = None
    categorie: Optional[str] = None
    email_auteur: Optional[str] = None

class ApprobationIn(BaseModel):
    proposition_id: int
    action: str

# ==========================================
# INITIALISATION
# ==========================================
Base.metadata.create_all(bind=engine)
app = FastAPI(title="API Markkanich Nouchi Pro - Avec Paiements")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ==========================================
# SEED AUTOMATIQUE AU DÉMARRAGE
# ==========================================
@app.on_event("startup")
def seed_database():
    db = next(get_db())
    try:
        count = db.query(func.count(MotNouchi.id)).scalar()
        if count == 0:
            if os.path.exists('nouchi_300.json'):
                with open('nouchi_300.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for i, item in enumerate(data):
                    db.add(MotNouchi(
                        mot=item['m'], prononciation=item['p'], definition=item['d'],
                        exemple=item['e'], origine=item['o'], categorie=item['c'],
                        is_premium=(i >= 20)
                    ))
                db.commit()
                print(f"✅ Base initialisée : {len(data)} mots ajoutés.")
            else:
                print("❌ Fichier nouchi_300.json introuvable.")
        else:
            print(f"ℹ️ Base déjà remplie ({count} mots).")
    except Exception as e:
        print(f"❌ Erreur seed : {e}")

# ==========================================
# FONCTIONS UTILITAIRES PAYSTACK
# ==========================================
def get_headers_paystack():
    return {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

def verifier_abonnement(utilisateur: Utilisateur) -> bool:
    if utilisateur.plan == "gratuit":
        return False
    if utilisateur.date_expiration and utilisateur.date_expiration > datetime.utcnow():
        return True
    return False

# ==========================================
# ENDPOINTS PUBLICS
# ==========================================
@app.get("/")
def read_root():
    return {
        "message": "API Markkanich Nouchi Pro 🇨🇮",
        "version": "4.0 - Avec paiements Paystack",
        "plans": {
            "gratuit": "20 mots, 5 recherches/jour",
            "premium": "263+ mots, illimité - 2 500 FCFA/mois",
            "pro": "API complète, usage commercial - 15 000 FCFA/mois"
        }
    }

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_users = db.query(func.count(Utilisateur.id)).scalar()
    total_premium = db.query(func.count(Utilisateur.id)).filter(Utilisateur.plan != "gratuit").scalar()
    return {
        "total_mots": db.query(func.count(MotNouchi.id)).scalar(),
        "total_categories": db.query(func.count(func.distinct(MotNouchi.categorie))).scalar(),
        "propositions_en_attente": db.query(func.count(Proposition.id)).filter(Proposition.statut == "en_attente").scalar(),
        "total_utilisateurs": total_users,
        "total_premium": total_premium
    }

@app.get("/mots/gratuits")
def mots_gratuits(db: Session = Depends(get_db)):
    return db.query(MotNouchi).filter(MotNouchi.is_premium == False).limit(20).all()

@app.get("/mots/complet")
def mots_complets(
    email: str = Query(...),
    q: Optional[str] = None,
    limite: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not utilisateur:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    if not verifier_abonnement(utilisateur):
        raise HTTPException(status_code=403, detail="Abonnement Premium requis")
    
    query = db.query(MotNouchi)
    if q:
        terme = f"%{q.lower()}%"
        query = query.filter(or_(func.lower(MotNouchi.mot).like(terme), func.lower(MotNouchi.definition).like(terme)))
    return query.limit(limite).all()

# ==========================================
# ENDPOINT SEED MANUEL (secours)
# ==========================================
@app.get("/seed")
def forcer_seed(db: Session = Depends(get_db)):
    try:
        count = db.query(func.count(MotNouchi.id)).scalar()
        if count > 0:
            return {"message": f"La base contient déjà {count} mots", "status": "ok"}
        if not os.path.exists('nouchi_300.json'):
            return {"message": "Fichier nouchi_300.json introuvable", "status": "error"}
        with open('nouchi_300.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i, item in enumerate(data):
            db.add(MotNouchi(
                mot=item['m'], prononciation=item['p'], definition=item['d'],
                exemple=item['e'], origine=item['o'], categorie=item['c'],
                is_premium=(i >= 20)
            ))
        db.commit()
        return {"message": f"Succès ! {len(data)} mots ajoutés.", "status": "success"}
    except Exception as e:
        return {"message": f"Erreur : {str(e)}", "status": "error"}

# ==========================================
# CONNEXION UTILISATEUR (CRÉATION AUTOMATIQUE)
# ==========================================
@app.post("/connexion")
def connexion(data: ConnexionUser, db: Session = Depends(get_db)):
    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
    if not utilisateur:
        utilisateur = Utilisateur(email=data.email, plan="gratuit")
        db.add(utilisateur)
        db.commit()
        db.refresh(utilisateur)
    
    return {
        "email": utilisateur.email,
        "nom": utilisateur.nom,
        "plan": utilisateur.plan,
        "abonnement_actif": verifier_abonnement(utilisateur),
        "date_expiration": utilisateur.date_expiration.isoformat() if utilisateur.date_expiration else None
    }

# ==========================================
# INITIALISATION PAIEMENT PAYSTACK
# ==========================================
@app.post("/initier-paiement")
def initier_paiement(data: InitPaiement, db: Session = Depends(get_db)):
    if not PAYSTACK_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Paystack non configuré. Ajoutez PAYSTACK_SECRET_KEY dans les variables d'environnement Render.")
    
    prix_plans = {
        "premium": 250000,  # 2 500 FCFA en centimes
        "pro": 1500000      # 15 000 FCFA en centimes
    }
    
    if data.plan not in prix_plans:
        raise HTTPException(status_code=400, detail="Plan invalide. Choisissez 'premium' ou 'pro'.")
    
    montant = prix_plans[data.plan]
    reference = f"MK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{data.email[:5]}"
    
    # Créer ou récupérer l'utilisateur
    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
    if not utilisateur:
        utilisateur = Utilisateur(email=data.email, nom=data.nom, plan="gratuit")
        db.add(utilisateur)
        db.commit()
        db.refresh(utilisateur)
    
    # Enregistrer le paiement en attente
    paiement = Paiement(
        utilisateur_id=utilisateur.id,
        reference=reference,
        montant=montant,
        plan=data.plan,
        statut="en_attente"
    )
    db.add(paiement)
    db.commit()
    
    # Appeler l'API Paystack
    try:
        response = requests.post(
            f"{PAYSTACK_URL}/transaction/initialize",
            headers=get_headers_paystack(),
            json={
                "email": data.email,
                "amount": montant,
                "reference": reference,
                "currency": "XOF",
                "metadata": {
                    "plan": data.plan,
                    "custom_fields": [
                        {"display_name": "Plan", "variable_name": "plan", "value": data.plan}
                    ]
                }
            }
        )
        result = response.json()
        
        if result.get("status"):
            return {
                "status": "success",
                "authorization_url": result["data"]["authorization_url"],
                "reference": reference,
                "access_code": result["data"]["access_code"]
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Erreur Paystack"))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erreur connexion Paystack: {str(e)}")

# ==========================================
# VÉRIFICATION PAIEMENT
# ==========================================
@app.post("/verifier-paiement")
def verifier_paiement(data: VerificationPaiement, db: Session = Depends(get_db)):
    try:
        response = requests.get(
            f"{PAYSTACK_URL}/transaction/verify/{data.reference}",
            headers=get_headers_paystack()
        )
        result = response.json()
        
        if result.get("status") and result["data"]["status"] == "success":
            reference = result["data"]["reference"]
            paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
            
            if paiement:
                paiement.statut = "success"
                utilisateur = db.query(Utilisateur).filter(Utilisateur.id == paiement.utilisateur_id).first()
                if utilisateur:
                    utilisateur.plan = paiement.plan
                    utilisateur.date_expiration = datetime.utcnow() + timedelta(days=30)
                    utilisateur.paystack_customer_code = result["data"]["customer"].get("customer_code")
                
                db.commit()
                return {
                    "status": "success",
                    "message": "Paiement réussi ! Abonnement activé pour 30 jours.",
                    "plan": paiement.plan,
                    "date_expiration": utilisateur.date_expiration.isoformat() if utilisateur else None
                }
        
        raise HTTPException(status_code=400, detail="Paiement non réussi")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erreur vérification: {str(e)}")

# ==========================================
# CONTRIBUTION & MODÉRATION
# ==========================================
@app.post("/contribuer", status_code=201)
def contribuer(data: ContributionIn, db: Session = Depends(get_db)):
    existant = db.query(MotNouchi).filter(func.lower(MotNouchi.mot) == data.mot_propose.lower()).first()
    if existant:
        raise HTTPException(status_code=400, detail="Ce mot existe déjà.")
    
    en_attente = db.query(Proposition).filter(
        func.lower(Proposition.mot_propose) == data.mot_propose.lower(),
        Proposition.statut == "en_attente"
    ).first()
    if en_attente:
        raise HTTPException(status_code=400, detail="Ce mot est déjà en attente de validation.")

    prop = Proposition(
        mot_propose=data.mot_propose,
        definition_proposee=data.definition_proposee,
        exemple=data.exemple,
        categorie=data.categorie,
        email_auteur=data.email_auteur
    )
    db.add(prop)
    db.commit()
    return {"message": "Merci ! Votre proposition est en attente de validation par nos experts."}

@app.post("/admin/approuver")
def approuver_proposition(data: ApprobationIn, db: Session = Depends(get_db)):
    prop = db.query(Proposition).filter(Proposition.id == data.proposition_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Proposition introuvable")
    
    if data.action == "approuver":
        nouveau_mot = MotNouchi(
            mot=prop.mot_propose,
            definition=prop.definition_proposee,
            exemple=prop.exemple,
            categorie=prop.categorie,
            origine="Contribution communautaire",
            is_premium=False
        )
        db.add(nouveau_mot)
        prop.statut = "approuve"
    elif data.action == "rejeter":
        prop.statut = "rejete"
    else:
        raise HTTPException(status_code=400, detail="Action invalide")
    
    db.commit()
    return {"message": f"Proposition {data.action}e avec succès"}

# ==========================================
# STATS ADMIN (pour voir les revenus)
# ==========================================
@app.get("/admin/stats-ventes")
def stats_ventes(db: Session = Depends(get_db)):
    total_premium = db.query(func.count(Utilisateur.id)).filter(Utilisateur.plan == "premium").scalar()
    total_pro = db.query(func.count(Utilisateur.id)).filter(Utilisateur.plan == "pro").scalar()
    revenus = (total_premium * 2500) + (total_pro * 15000)
    return {
        "abonnés_premium": total_premium,
        "abonnés_pro": total_pro,
        "revenus_mensuels_fcfa": revenus,
        "revenus_mensuels_eur": round(revenus / 655.957, 2)
    }
