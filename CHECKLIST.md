# Checklist de refonte de FestiPlan

## 1. Analyser l'architecture initiale
- [x] Démarrer l'application et parcourir les endpoints disponibles dans Swagger (`/docs`)
- [x] Repérer les fichiers qui reçoivent les requêtes HTTP
- [x] Décrire les responsabilités actuelles des routes, services, modèles et repositories
- [x] Suivre les dépendances entre ces composants et le sens de leurs appels
- [x] Localiser les règles métier et le code qui lit/écrit en base
- [x] Repérer les dépendances directes du métier à FastAPI, Pydantic et SQLAlchemy
- [x] Identifier les problèmes de testabilité, les risques d'incohérence et les responsabilités mal placées
- [x] Illustrer le diagnostic par au moins un exemple concret tiré du code
- [x] Exécuter les tests existants et noter leur résultat avant les changements
- [x] Reproduire les trois défauts initiaux et noter pour chacun les étapes et le résultat observé
- [x] Rédiger un diagnostic succinct de l'architecture initiale

## 2. Définir le modèle métier avec DDD
- [x] Distinguer les entités (Festival, Concert, Artiste, Scène, Incident) selon leur identité et leur cycle de vie
- [x] Identifier les objets-valeurs pertinents (créneau horaire, période du festival, besoins/équipements techniques)
- [x] Définir les invariants métier, notamment la validité d'un créneau
- [x] Décider où chaque invariant est garanti : objet-valeur, entité/agrégat, politique de domaine ou cas d'utilisation
- [x] Proposer les frontières d'agrégats sans regrouper tous les objets ni créer automatiquement un agrégat par classe
- [x] Justifier les frontières retenues et le rôle des racines d'agrégat dans la cohérence
- [x] Identifier les événements de domaine utiles (par exemple `ConcertRescheduled`) et le fait métier qu'ils représentent
- [x] Distinguer explicitement commande, cas d'utilisation, événement de domaine et mécanisme technique réagissant à l'événement
- [x] Rédiger la première modélisation du domaine et ses justifications comme livrable intermédiaire

## 3. Organiser l'architecture hexagonale
- [x] Isoler les entités et règles du domaine de FastAPI, Pydantic et SQLAlchemy
- [x] Créer les cas d'utilisation pertinents (programmation/déplacement, publication, incident et gestion des référentiels)
- [x] Définir les ports entrants dans `app/application_ports.py`
- [x] Définir les ports sortants de persistance et notification dans `app/ports.py`
- [x] Implémenter les adaptateurs entrants HTTP FastAPI dans `app/api/`
- [x] Implémenter les adaptateurs SQLAlchemy pour les contrats de persistance
- [x] Implémenter l'adaptateur de notification simulée
- [x] Créer le point de composition et d'injection dans `app/composition.py`
- [x] Vérifier que les cas d'utilisation reçoivent les ports et n'instancient pas eux-mêmes de dépendances techniques
- [x] Vérifier la distinction entre contrats de ports et implémentations d'adaptateurs

## 4. Refactoriser le code existant
- [x] Commencer par une fonctionnalité délimitée, de préférence le déplacement d'un concert
- [x] Décrire son comportement initial, ses dépendances et les tests nécessaires
- [x] Écrire les tests de caractérisation/non-régression avant de modifier le parcours
- [x] Isoler les règles métier de déplacement et de disponibilité du planning
- [x] Créer les cas d'utilisation et définir leurs ports nécessaires
- [x] Implémenter les adaptateurs nécessaires et adapter les contrôleurs HTTP pour appeler les ports entrants
- [x] Exécuter les tests ciblés puis vérifier que l'API reste exécutable
- [x] Appliquer progressivement le découpage aux autres fonctionnalités
- [x] Vérifier les comportements avant/après migration et corriger les régressions

## 5. Corriger les trois défauts initiaux
- [x] Défaut 1 : refuser un chevauchement avec un autre concert sur la même scène
- [x] Défaut 1 : refuser le chevauchement d'un même artiste, même si les concerts sont sur des scènes différentes
- [x] Défaut 1 : accepter un déplacement valide et vérifier que le concert déplacé n'est pas comparé à lui-même
- [x] Défaut 2 : séparer la réussite de la modification métier du succès de l'envoi de notification
- [x] Défaut 2 : choisir et documenter un comportement proportionné à l'échec de notification (sans obligation d'une gestion asynchrone avancée)
- [x] Défaut 2 : garantir que la réponse HTTP ne laisse pas croire que la modification a échoué si elle est déjà persistée
- [x] Défaut 3 : représenter l'état du planning avec `FestivalStatus` et la transition préparation → publié
- [x] Défaut 3 : définir le comportement d'un déplacement ordinaire après publication (refus, dépublication ou procédure métier dédiée)
- [x] Défaut 3 : n'autoriser les changements post-publication que selon la procédure choisie
- [x] Documenter les scénarios de reproduction, la correction retenue et les tests de non-régression des trois défauts

## 6. Respecter les dix règles métier
- [x] R1 — Refuser un créneau dont la fin est égale ou antérieure au début
- [x] R2 — Refuser tout chevauchement de concerts sur une même scène
- [x] R3 — Refuser tout chevauchement pour un même artiste, y compris sur plusieurs scènes
- [x] R4 — Vérifier l'existence du festival, de l'artiste et de la scène, et l'appartenance de la scène au festival concerné
- [x] R5 — Vérifier que les équipements requis par l'artiste sont disponibles sur la scène
- [x] R6 — Vérifier que le concert commence et se termine dans la période du festival
- [x] R7 — Bloquer les modifications ordinaires d'un planning publié et appliquer la procédure explicite retenue
- [x] R8 — Valider l'ensemble des concerts selon les règles de programmation avant publication
- [x] R9 — Refuser une capacité de scène, une durée ou toute quantité obligatoire nulle ou négative
- [x] R10 — Vérifier l'existence du concert associé à l'incident et refuser une description vide ou composée d'espaces
- [x] Préciser où les règles sont garanties; R10 vérifie existence et description depuis le cas d'utilisation, via un port

## 7. Mettre en place les tests
- [x] Tester le domaine sans démarrer FastAPI ni se connecter à SQLite
- [x] Couvrir les créneaux invalides, les invariants, les chevauchements et les transitions d'état
- [x] Tester les cas d'utilisation de programmation et de déplacement, y compris refus et déplacement valide
- [x] Tester la publication, la validation de tous les concerts et la protection d'un planning publié
- [x] Tester la gestion des erreurs et le comportement si la notification échoue après persistance
- [x] Utiliser des repositories en mémoire pour tester les décisions applicatives et interactions avec les ports
- [x] Tester les adaptateurs HTTP et les réponses des routes
- [x] Tester les adaptateurs de persistance avec la base de données
- [x] Ajouter les tests de non-régression explicites pour chacun des trois défauts reproduits
- [x] Exécuter les tests ciblés puis la suite complète `pytest` après la migration hexagonale et l'état métier (49 tests réussis le 8 novembre 2026)
- [x] Corriger les échecs et confirmer que les tests protègent les comportements attendus, pas seulement des lignes de code

## 8. Réaliser le diagramme UML de composants
- [x] Représenter le domaine et les services/opérations applicatives actuellement présents
- [x] Représenter les ports entrants/sortants, les cas d'utilisation et les adaptateurs
- [x] Montrer l'implémentation des ports par les adaptateurs concrets
- [x] Montrer le point de composition et le flux d'une requête jusqu'à la persistance
- [x] Montrer les dépendances de persistance et de notification réellement présentes
- [x] Vérifier que le diagramme décrit l'architecture hexagonale effectivement livrée
- [x] Générer les versions SVG et vérifier le rendu PlantUML

## 9. Réaliser le diagramme UML de séquence
- [x] Choisir le déplacement d'un concert comme scénario
- [x] Représenter la requête HTTP, la route entrante et le SchedulingService
- [x] Représenter les appels via ports de persistance et adaptateur SQLAlchemy
- [x] Représenter les validations métier, les refus possibles et les réponses HTTP associées
- [x] Montrer l'enregistrement en base avant l'envoi de notification
- [x] Représenter le succès et l'échec de notification après persistance
- [x] Montrer le statut de notification et la réponse HTTP finale dans chaque scénario

## 10. Documenter l'architecture
- [x] Expliquer les principaux défauts de l'architecture initiale avec des exemples observés (`docs/architecture/diagnostic-initial.md`)
- [x] Décrire les responsabilités et dépendances des couches actuelles (`docs/architecture/diagnostic-initial.md`)
- [x] Présenter les ports entrants/sortants et adaptateurs effectivement implémentés (`README.md`, diagramme de composants)
- [x] Présenter les entités, objets-valeurs, invariants et frontières d'agrégats proposées (`docs/architecture/modele-metier.md`)
- [x] Expliquer où les règles métier sont garanties et leurs limites (`docs/architecture/regles-metier.md`)
- [x] Expliquer les corrections des trois défauts, l'échec de notification et la protection du planning publié (`diagnostic-initial.md`, README)
- [x] Présenter les tests et leur couverture des règles (`regles-metier.md`, README)
- [x] Expliquer les compromis et limites restantes (`modele-metier.md`, `diagnostic-initial.md`)
- [x] Illustrer les conséquences des choix par les défauts reproduits et les corrections apportées
- [x] Rassembler diagnostic, modèle métier, règles, tests et limites dans `docs/architecture/note-architecture.md`

## 11. Mettre à jour le README
- [x] Indiquer les prérequis (Python 3.11+ et environnement virtuel)
- [x] Documenter la création/activation de l'environnement et l'installation via `pip install -r requirements.txt`
- [x] Documenter la configuration éventuelle (`.env`) et l'initialisation avec `python -m app.seed`
- [x] Avertir que l'initialisation peut réinitialiser les données de la base configurée et doit être réservée au développement
- [x] Documenter le démarrage via `uvicorn app.main:app --reload`
- [x] Documenter l'accès à Swagger (`http://127.0.0.1:8000/docs`)
- [x] Documenter l'exécution de la suite avec `pytest`

## 12. Préparer le rendu final
- [x] Livrable 1 — Code refactorisé et exécutable (suite et démarrage à valider avant le rendu)
- [x] Livrable 2 — Tests unitaires, applicatifs et d'intégration pertinents
- [x] Livrable 3 — Tests de non-régression des trois défauts
- [x] Livrable intermédiaire — Première modélisation DDD expliquée (entités, objets-valeurs, invariants, agrégats)
- [x] Livrable 4 — Diagramme UML de composants conforme à l'architecture réelle
- [x] Livrable 5 — Diagramme UML de séquence du déplacement d'un concert
- [x] Livrable 6 — Note d'architecture justifiant les choix, compromis et limites (`docs/architecture/note-architecture.md`)
- [x] Livrable 7 — README mis à jour
- [x] Relancer la suite complète de tests après migration hexagonale et état métier (49 tests réussis le 8 novembre 2026)
- [x] Démarrer l'API et vérifier en HTTP la santé, Swagger, OpenAPI et les routes de lecture
- [x] Vérifier les réponses d'erreur attendues (404 pour publication inconnue, 422 pour corps invalide)
- [x] Vérifier l'installation depuis zéro dans un venv temporaire Python 3.13 (pip check OK, 49 tests réussis, API HTTP vérifiée)
- [ ] Préparer le dépôt GitHub ou l'archive du rendu selon les modalités du professeur

## Repères pour la grille d'évaluation

| Critère | Preuves à consulter |
|---|---|
| Diagnostic initial | [Diagnostic de l'architecture initiale](docs/architecture/diagnostic-initial.md) — architecture, dépendances, exemples et reproduction des trois défauts |
| Modélisation DDD | [Modélisation métier](docs/architecture/modele-metier.md) — entités, objets-valeurs, invariants, agrégats et événements |
| Architecture hexagonale | [Note d'architecture](docs/architecture/note-architecture.md), `app/domain/`, `app/application_ports.py`, `app/ports.py`, `app/adapters/`, `app/api/` et `app/composition.py` |
| Correction des trois défauts | [Diagnostic initial](docs/architecture/diagnostic-initial.md) et tests de non-régression dans `tests/test_scheduling.py` et `tests/test_publication.py` |
| Règles métier R1 à R10 | [Règles métier](docs/architecture/regles-metier.md) et tests du domaine et des cas d'utilisation dans `tests/` |
| Stratégie de tests | [Note d'architecture](docs/architecture/note-architecture.md), `tests/test_domain_scheduling.py`, `tests/test_application_services.py` et tests d'API/intégration; exécution : `pytest` |
| UML de composants | [Diagramme de composants PlantUML](docs/architecture/diagramme-composants.puml) et [rendu SVG](docs/architecture/diagramme-composants.svg) |
| UML de séquence | [Diagramme de séquence PlantUML](docs/architecture/diagramme-sequence-deplacement.puml) et [rendu SVG](docs/architecture/diagramme-sequence-deplacement.svg) |
| Note d'architecture | [Note d'architecture](docs/architecture/note-architecture.md) |
| README et exécution | [README](README.md) — installation, initialisation, démarrage, Swagger et tests |
