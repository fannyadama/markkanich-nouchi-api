import json
import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, or_
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from database import get_db, engine, Base

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
# SCHÉMAS PYDANTIC
# ==========================================
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
app = FastAPI(title="API Markkanich Nouchi Pro")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Seed automatique au démarrage (avec meilleure gestion des erreurs)
@app.on_event("startup")
def seed_database_startup():
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
                print(f"✅ Base initialisée avec succès : {len(data)} mots ajoutés.")
            else:
                print("❌ Fichier nouchi_300.json introuvable dans le répertoire de travail.")
        else:
            print(f"ℹ️ Base de données déjà remplie ({count} mots). Seed ignoré.")
    except Exception as e:
        print(f"❌ Erreur lors du seed au démarrage : {e}")

# ==========================================
# ENDPOINTS PUBLICS
# ==========================================
@app.get("/")
def read_root():
    return {"message": "API Markkanich Nouchi Pro 🇨🇮", "version": "3.0"}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_mots": db.query(func.count(MotNouchi.id)).scalar(),
        "total_categories": db.query(func.count(func.distinct(MotNouchi.categorie))).scalar(),
        "propositions_en_attente": db.query(func.count(Proposition.id)).filter(Proposition.statut == "en_attente").scalar()
    }

@app.get("/mots/gratuits")
def mots_gratuits(db: Session = Depends(get_db)):
    return db.query(MotNouchi).filter(MotNouchi.is_premium == False).limit(20).all()

@app.get("/mots/complet")
def mots_complets(q: Optional[str] = None, limite: int = Query(50, le=100), db: Session = Depends(get_db)):
    query = db.query(MotNouchi)
    if q:
        terme = f"%{q.lower()}%"
        query = query.filter(or_(func.lower(MotNouchi.mot).like(terme), func.lower(MotNouchi.definition).like(terme)))
    return query.limit(limite).all()

# ==========================================
# ENDPOINT MANUEL DE REMPLISSAGE (LE BOUTON DE SECOURS)
# ==========================================
@app.get("/seed")
def forcer_seed(db: Session = Depends(get_db)):
    """Endpoint manuel pour forcer le remplissage de la base"""
    try:
        count = db.query(func.count(MotNouchi.id)).scalar()
        if count > 0:
            return {"message": f"La base contient déjà {count} mots", "status": "ok"}
        
        if not os.path.exists('nouchi_300.json'):
            return {"message": "Erreur: Le fichier nouchi_300.json est introuvable sur le serveur.", "status": "error"}
            
        with open('nouchi_300.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for i, item in enumerate(data):
            db.add(MotNouchi(
                mot=item['m'], prononciation=item['p'], definition=item['d'],
                exemple=item['e'], origine=item['o'], categorie=item['c'],
                is_premium=(i >= 20)
            ))
        db.commit()
        return {"message": f"Succès ! {len(data)} mots ajoutés à la base de données.", "status": "success"}
    except Exception as e:
        return {"message": f"Erreur lors du remplissage : {str(e)}", "status": "error"}

# ==========================================
# CONTRIBUTION & MODÉRATION
# ==========================================
@app.post("/contribuer", status_code=201)
def contribuer(data: ContributionIn, db: Session = Depends(get_db)):
    existant = db.query(MotNouchi).filter(func.lower(MotNouchi.mot) == data.mot_propose.lower()).first()
    if existant:
        raise HTTPException(status_code=400, detail="Ce mot existe déjà dans le dictionnaire.")
    
    en_attente = db.query(Proposition).filter(func.lower(Proposition.mot_propose) == data.mot_propose.lower(), Proposition.statut == "en_attente").first()
    if en_attente:
        raise HTTPException(status_code=400, detail="Ce mot est déjà en attente de validation.")

    prop = Proposition(
        mot_propose=data.mot_propose, definition_proposee=data.definition_proposee,
        exemple=data.exemple, categorie=data.categorie, email_auteur=data.email_auteur
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
            mot=prop.mot_propose, definition=prop.definition_proposee,
            exemple=prop.exemple, categorie=prop.categorie, origine="Contribution communautaire", is_premium=False
        )
        db.add(nouveau_mot)
        prop.statut = "approuve"
    elif data.action == "rejeter":
        prop.statut = "rejete"
    else:
        raise HTTPException(status_code=400, detail="Action invalide")
    
    db.commit()
    return {"message": f"Proposition {data.action}e avec succès"}
