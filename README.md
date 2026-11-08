# FestiPlan

API pédagogique FastAPI de gestion d'un festival de musique fictif. Le domaine, les cas d'utilisation et les adaptateurs sont séparés selon une architecture hexagonale, avec une migration réalisée progressivement.

Les règles de programmation sont indépendantes de FastAPI et SQLAlchemy. Les routes utilisent des ports entrants, les cas d'utilisation reçoivent des ports sortants et le câblage concret est centralisé dans `app/composition.py`.

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
```

Initialisez la base et les données fictives :
```bash
python -m app.seed
```

> **Attention :** `python -m app.seed` supprime et recrée les données présentes dans la base configurée. Utilisez cette commande uniquement dans un environnement de développement et après avoir vérifié la valeur de `FESTIPLAN_DATABASE_URL`.

Démarrez l'API :
```bash
uvicorn app.main:app --reload
```

Documentation interactive Swagger : http://127.0.0.1:8000/docs

Tests : `pytest` (ou `.\.venv\Scripts\python.exe -m pytest` sous Windows). La suite couvre le domaine, les cas d'utilisation avec repositories en mémoire et les adaptateurs HTTP/persistance.

Par défaut, SQLite crée `festiplan.db` dans le dossier courant. Copier `.env.example` vers `.env` si nécessaire.

## Données
Festival fictif **Hellforge Open Air**, du 18 au 20 juin 2027. Scènes : Mainstage, Warzone, Valley et Temple. Les groupes, horaires et capacités sont inventés ; seule l'ambiance générale est inspirée des festivals metal multi-scènes.

## Défauts observés dans le dépôt initial
1. Déplacer un concert sur un créneau occupé sur la même scène : le parcours de déplacement ne vérifiait pas les conflits.
2. Définir `FESTIPLAN_FAIL_NOTIFICATIONS=true`, déplacer un concert, puis consulter son créneau : l'API pouvait répondre 500 alors que le déplacement était déjà enregistré.
3. Publier le festival puis déplacer un concert par l'endpoint ordinaire : le statut publié n'était pas protégé.

Ces défauts ont été reproduits et documentés avant leur correction. Leur correction et l'architecture actuelle sont décrites ci-dessous.

## Comportement métier
- Le déplacement vérifie les conflits de scène et d'artiste, y compris entre festivals, l'équipement requis, la période du festival et l'état de publication.
- Un planning publié refuse les opérations ordinaires de programmation, déplacement et annulation.
- Si l'envoi de notification échoue après l'enregistrement du déplacement, l'API conserve une réponse de succès et renvoie `X-Notification-Status: failed`. L'échec technique est consigné dans les logs; le déplacement reste enregistré.
- Les règles de créneau et de conflit sont couvertes par des tests unitaires du domaine, en plus des tests API de non-régression.

## Architecture

- `app/domain/` contient les entités métier et règles pures.
- `app/application_ports.py` définit les contrats entrants des cas d'utilisation.
- `app/ports.py` définit les contrats sortants de persistance et notification.
- `app/services/` contient les cas d'utilisation; ils dépendent des ports, pas de SQLAlchemy ni de FastAPI.
- `app/adapters/` contient les implémentations SQLAlchemy et la notification simulée.
- `app/api/` contient les adaptateurs HTTP. Ils ne manipulent pas directement la session ni les modèles ORM.
- `app/composition.py` construit les cas d'utilisation avec les adaptateurs concrets et les sessions injectées.

## Documentation d'architecture
- [Note d'architecture](docs/architecture/note-architecture.md) — synthèse du diagnostic, des choix, des règles, des tests et limites.
- [Diagnostic de l'architecture initiale](docs/architecture/diagnostic-initial.md) — responsabilités, dépendances, endpoints et reproduction des défauts.
- [Modélisation métier actuelle et cible](docs/architecture/modele-metier.md) — objets-valeurs, invariants, frontières d'agrégats proposées et limites restantes.
- [Règles métier R1–R10](docs/architecture/regles-metier.md) — emplacement des règles, services concernés et tests de référence.
- [Diagramme UML de composants](docs/architecture/diagramme-composants.puml) ([SVG](docs/architecture/diagramme-composants.svg)) — ports, cas d'utilisation, adaptateurs et composition.
- [Diagramme UML de séquence](docs/architecture/diagramme-sequence-deplacement.puml) ([SVG](docs/architecture/diagramme-sequence-deplacement.svg)) — déplacement d'un concert et notification.
- [Checklist de refactorisation](CHECKLIST.md) — avancement des tâches du sujet.

La suite complète de tests est lancée avec `pytest`. Les tests applicatifs utilisent aussi des repositories en mémoire afin de vérifier les cas d'utilisation sans FastAPI ni SQLite.
