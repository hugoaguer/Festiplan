# FestiPlan

API pédagogique FastAPI de gestion d'un festival metal fictif. Le code sépare les routes, les services/cas d'usage, les ports de repository et les repositories SQLAlchemy. Les règles de programmation des concerts sont regroupées dans le domaine, avec un mapper dédié entre le modèle métier et le modèle de persistance. Le projet reste un exemple pédagogique et ne doit pas être utilisé en production.

## Fonctionnalités
- Festivals, artistes, scènes et concerts
- Consultation du planning, déplacement et annulation de concerts
- Publication d'un festival et déclaration d'incidents
- Notifications simulées, avec échec configurable

## Installation (Python 3.11+)
```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1 ; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
```
Documentation : http://127.0.0.1:8000/docs
Tests : `pytest`

Par défaut, SQLite crée `festiplan.db` dans le dossier courant. Copier `.env.example` vers `.env` si nécessaire.

## Données
Festival fictif **Hellforge Open Air**, du 18 au 20 juin 2027. Scènes : Mainstage, Warzone, Valley et Temple. Les groupes, horaires et capacités sont inventés ; seule l'ambiance générale est inspirée des festivals metal multi-scènes.

## Garanties métier
- Les conflits de créneaux, la période du festival, l'équipement requis et l'état de publication sont vérifiés lors de la création, du déplacement et de la publication d'un planning.
- Un échec de notification est journalisé sans annuler une modification déjà enregistrée.
- Un planning publié ne peut plus être modifié par les opérations ordinaires.
- La création d'un incident vérifie l'existence du concert ; son horodatage est renseigné par défaut s'il n'est pas fourni.

Les tests couvrent les règles du domaine, le mapping et le repository des concerts, les parcours API et les régressions métier.
