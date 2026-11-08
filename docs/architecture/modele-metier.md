# Modélisation métier FestiPlan

Ce document décrit les entités et règles indépendantes introduites dans le domaine, ainsi que les frontières d'agrégats proposées pour la suite. Il sépare explicitement le code présent des choix métier qui restent à préciser.

## Langage métier

- **Festival** : événement borné par une période, qui possède des scènes et un planning.
- **Scène** : lieu d'un concert, rattaché à un festival, avec une capacité et des équipements.
- **Artiste** : groupe ou interprète ayant des besoins techniques.
- **Concert** : représentation d'un artiste sur une scène dans un créneau.
- **Planning** : ensemble des concerts d'un festival, préparé puis publié.
- **Incident** : signalement associé à un concert existant.
- **Notification** : effet secondaire informant un destinataire d'un changement; ce n'est pas une règle du domaine.

## Entités et objets-valeurs

Les identifiants persistés du projet (`Festival.id`, `Stage.id`, etc.) donnent une identité aux concepts Festival, Scène, Artiste, Concert et Incident. `app/domain/entities.py` fournit désormais des représentations métier indépendantes; les adaptateurs SQLAlchemy convertissent les lignes ORM en ces entités.

Le domaine de programmation dans `app/domain/scheduling.py` comprend :

- `TimeSlot(start, end)`, objet-valeur immuable qui refuse `end <= start` et définit le chevauchement selon des intervalles semi-ouverts. Deux concerts dont l'un finit exactement quand l'autre commence ne se chevauchent donc pas.
- `ScheduledConcert`, représentation sans dépendance à SQLAlchemy qui porte les références, le créneau, la période du festival et les équipements nécessaires aux validations.

Les périodes de Festival et les ensembles de besoins/équipements sont des objets-valeurs pertinents à extraire dans une prochaine étape. Ils sont encore représentés par des champs `datetime` et des chaînes séparées par des virgules dans les modèles ORM actuels.

## Invariants et emplacement visé

| Règle | Protection actuelle | Emplacement cible |
| --- | --- | --- |
| Le créneau se termine après son début (R1) | `TimeSlot`, utilisé lors des validations de programmation | Objet-valeur `TimeSlot` |
| Pas de chevauchement sur une scène (R2) | `ensure_no_conflicts`, appelée par `SchedulingService` | Politique de domaine du planning |
| Un artiste ne joue pas simultanément ailleurs (R3) | `ensure_no_conflicts` sur les concerts actifs chargés via ports | Politique de domaine du planning |
| Festival, artiste et scène existent et la scène appartient au festival (R4) | `SchedulingService` charge via ports; `validate_concert_assignment` contrôle l'appartenance | Cas d'utilisation pour les références, domaine pour l'appartenance |
| Les besoins techniques sont disponibles (R5) | `validate_concert_assignment` sur les entités métier | Politique métier du domaine |
| Le concert est dans la période du festival (R6) | `validate_concert_assignment` sur les entités métier | Politique métier entre `TimeSlot` et période du festival |
| Planning publié protégé (R7) | `FestivalStatus` et `ensure_schedule_is_editable`, appelés avant création, déplacement ou annulation | Transition explicite du planning dans l'entité Festival |
| Tous les concerts valides avant publication (R8) | `PublicationService` reconstruit le planning, appelle `validate_full_schedule` puis persiste l'état | Cas d'utilisation de publication et domaine |
| Capacité et durée positives (R9) | `StageService` appelle `validate_capacity`; `TimeSlot` refuse les durées invalides | Domaine, appelé par les cas d'utilisation |
| Incident valide (R10) | `IncidentService` valide le texte et vérifie l'existence du concert via `ConcertRepository` | Cas d'utilisation et domaine |

Les validations de forme HTTP restent dans Pydantic, mais elles ne remplacent pas les garanties métier : les cas d'utilisation valident eux aussi les invariants.

L'état du festival est codé par `FestivalStatus` (`PREPARATION`, `PUBLISHED`). `Festival.publish_schedule()` autorise uniquement la transition préparation vers publié; `Festival.ensure_schedule_is_editable()` refuse les modifications d'un planning publié. Il n'existe pas de transition de dépublication.

## Frontières d'agrégats proposées

1. **Planning de festival** — Festival comme racine logique pour l'état publié et les changements autorisés. Les Concerts sont des membres ou des références contrôlées par le planning. Les règles de conflits nécessitent de considérer les concerts concernés et d'exclure le concert modifié.
2. **Concert** — identité et créneau d'une représentation. Si le planning devenait volumineux ou fortement concurrent, un concert pourrait être un agrégat séparé et une politique de domaine vérifierait les conflits avec un instantané des disponibilités.
3. **Artiste** et **Scène** — entités référencées par identifiant depuis la programmation. Leur contenu complet n'a pas besoin d'être chargé comme partie d'un même agrégat à chaque déplacement.
4. **Incident** — enregistrement indépendant qui référence un identifiant de concert existant; sa création est validée par un cas d'utilisation.

Pour le projet pédagogique, le Planning/Festival est un point de départ cohérent car la publication et l'ordonnancement sont exprimés par festival. Les entités métier sont séparées des modèles ORM, mais l'implémentation ne matérialise pas encore les frontières d'agrégats proposées. La cohérence en cas de modifications concurrentes nécessiterait également une stratégie transactionnelle/optimiste explicite.

## Commandes, cas d'utilisation, événements et techniques

- **Commande** : demande de programmer ou déplacer un concert, publier un planning, ou enregistrer un incident; elle exprime une intention.
- **Cas d'utilisation** : orchestre les lectures nécessaires, appelle les règles de domaine, persiste les changements et détermine le résultat.
- **Événement de domaine** : fait accompli, par exemple `ConcertRescheduled(concert_id, previous_slot, new_slot)`. Il n'est pas encore implémenté dans le dépôt.
- **Réaction technique** : envoi d'une notification après persistance. Aujourd'hui l'appel est synchrone; un échec connu est journalisé et exposé par l'en-tête HTTP sans annuler le déplacement déjà commité. Aucun mécanisme asynchrone ou outbox n'est encore en place.

## Étapes de modélisation restantes

- Extraire des objets-valeurs de période du festival et d'équipements.
- Décider formellement si le planning est un agrégat avec ses concerts ou si les règles de disponibilité sont une politique de domaine.
- Renforcer les garanties transactionnelles en cas de modifications concurrentes.

Les cas d'utilisation, ports entrants et sortants, adaptateurs HTTP, SQLAlchemy et notification sont en place. L'état du planning est typé et sa transition vers la publication est explicite. Les frontières d'agrégats et la cohérence concurrente restent à approfondir.
