import json
import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, func, or_
from typing import Optional
from pydantic import BaseModel
from database import get_db, engine, Base

class MotNouchi(Base):
    __tablename__ = "mots_nouchi"
    id = Column(Integer, primary_key=True, index=True)
    mot = Column(String, unique=True, index=True, nullable=False)
    prononciation = Column(String)
    definition = Column(Text)
    exemple = Column(Text)
    origine = Column(String)
    categorie = Column(String, index=True)
    nb_consultations = Column(Integer, default=0)

class ContributionIn(BaseModel):
    mot_propose: str
    definition_proposee: str
    exemple: Optional[str] = None
    categorie: Optional[str] = None
    auteur_email: Optional[str] = None

# Créer les tables
Base.metadata.create_all(bind=engine)
app = FastAPI(title="API Markkanich Nouchi")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def read_root():
    return {"message": "API Markkanich Nouchi en ligne 🇨🇮"}

@app.get("/mots")
def get_mots(q: Optional[str] = None, categorie: Optional[str] = None, page: int = 1, limite: int = 50, db: Session = Depends(get_db)):
    query = db.query(MotNouchi)
    if q:
        terme = f"%{q.lower()}%"
        query = query.filter(or_(func.lower(MotNouchi.mot).like(terme), func.lower(MotNouchi.definition).like(terme)))
    if categorie:
        query = query.filter(MotNouchi.categorie == categorie)
    return query.offset((page - 1) * limite).limit(limite).all()

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_mots": db.query(func.count(MotNouchi.id)).scalar(),
        "total_categories": db.query(func.count(func.distinct(MotNouchi.categorie))).scalar()
    }

@app.post("/contribuer", status_code=201)
def contribuer(data: ContributionIn, db: Session = Depends(get_db)):
    existant = db.query(MotNouchi).filter(func.lower(MotNouchi.mot) == data.mot_propose.lower()).first()
    if existant:
        raise HTTPException(status_code=400, detail="Ce mot existe déjà.")
    nouveau = MotNouchi(mot=data.mot_propose, definition=data.definition_proposee, exemple=data.exemple, categorie=data.categorie, origine="Contribution utilisateur")
    db.add(nouveau)
    db.commit()
    return {"message": "Merci ! Mot ajouté avec succès."}

# ==========================================
# NOUVEAU ENDPOINT POUR FORCER LE REMPLISSAGE
# ==========================================
@app.get("/seed")
def forcer_seed(db: Session = Depends(get_db)):
    """Endpoint pour forcer le remplissage de la base avec les 300 mots"""
    try:
        # Vérifier si la base est déjà remplie
        count = db.query(func.count(MotNouchi.id)).scalar()
        if count > 0:
            return {"message": f"La base contient déjà {count} mots", "status": "ok"}
        
        # Charger et insérer les mots depuis le fichier JSON
        with open('nouchi_300.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            mot = MotNouchi(
                mot=item['m'], 
                prononciation=item['p'], 
                definition=item['d'], 
                exemple=item['e'], 
                origine=item['o'], 
                categorie=item['c']
            )
            db.add(mot)
        
        db.commit()
        return {"message": f"Succès ! {len(data)} mots ajoutés à la base de données.", "status": "success"}
    except Exception as e:
        return {"message": f"Erreur lors du remplissage : {str(e)}", "status": "error"}
