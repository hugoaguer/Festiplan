# Note d'architecture — FestiPlan

## Objectif et périmètre

FestiPlan est une API pédagogique de gestion de festivals, scènes, artistes, concerts et incidents. Cette note rassemble le diagnostic initial, les choix DDD, l'architecture hexagonale retenue, les corrections métier et les limites connues. Elle décrit le code livré; les évolutions explicitement indiquées comme limites ne sont pas présentées comme déjà implémentées.

## Diagnostic initial

L'application était un monolithe FastAPI utilisant SQLAlchemy et SQLite. Le problème n'était pas le monolithe lui-même, mais le mélange de responsabilités :

- Certaines routes, notamment la lecture d'un concert et la gestion des incidents, interrogeaient ou modifiaient directement la base.
- Les services recevaient des sessions SQLAlchemy et construisaient leurs repositories et services de notification.
- Les modèles ORM étaient employés directement par le métier et renvoyés dans les réponses HTTP.
- Les règles métier n'étaient pas toutes vérifiées par le déplacement d'un concert.

Les tests initiaux couvraient peu ces règles. Le diagnostic et les scénarios de reproduction sont détaillés dans [diagnostic-initial.md](./diagnostic-initial.md).

## Découpage retenu

Le code suit une architecture hexagonale avec dépendances dirigées vers le domaine :

| Couche | Responsabilité | Emplacement |
|---|---|---|
| Domaine | Entités métier, état du festival et règles invariantes | `app/domain/` |
| Ports entrants | Contrats des actions offertes aux adaptateurs | `app/application_ports.py` |
| Application | Orchestration des cas d'utilisation et décisions applicatives | `app/services/` |
| Ports sortants | Contrats de lecture/écriture et notification | `app/ports.py` |
| Adaptateurs sortants | Conversion ORM, persistance SQLAlchemy et notification simulée | `app/adapters/` |
| Adaptateurs entrants | Validation et traduction HTTP vers les cas d'utilisation | `app/api/` |
| Composition | Instanciation et injection des implémentations concrètes | `app/composition.py` |

Les cas d'utilisation ne connaissent ni FastAPI, ni Pydantic, ni SQLAlchemy. Les routes dépendent des contrats entrants; les services dépendent des ports sortants. Les adaptateurs SQLAlchemy convertissent les lignes ORM en entités du domaine. Les tests applicatifs substituent des repositories et notifications en mémoire.

## Modèle métier et état du planning

Les concepts Festival, Artist, Stage, Concert et Incident ont des entités métier séparées des modèles ORM. Le domaine de programmation utilise `TimeSlot` et `ScheduledConcert` pour vérifier durée, période, équipements, appartenance de la scène et chevauchements. Les choix détaillés de vocabulaire et de frontières d'agrégats sont dans [modele-metier.md](./modele-metier.md).

L'état du planning d'un festival est représenté par `FestivalStatus`, une énumération composée de :

- `PREPARATION` (`preparation`) : le planning peut être modifié et soumis à validation;
- `PUBLISHED` (`published`) : le planning est publié et les opérations ordinaires de création, déplacement et annulation sont refusées.

La seule transition prévue est `PREPARATION -> PUBLISHED`, portée par `Festival.publish_schedule()`. Cette opération refuse la publication depuis un état autre que la préparation. Il n'existe pas de dépublication. Le statut stocké en base reste une chaîne compatible avec les valeurs actuelles; l'adaptateur la convertit en énumération métier. Les valeurs existantes `preparation` et `published` ne nécessitent donc pas de migration de données.

## Règles métier et garanties

| Règle | Garantie principale |
|---|---|
| R1 — fin strictement après début | `TimeSlot` |
| R2/R3 — conflits de scène ou d'artiste | Politique domaine `ensure_no_conflicts`, alimentée par le cas d'utilisation |
| R4 — références présentes et scène du bon festival | Lecture via ports dans le cas d'utilisation, appartenance validée par le domaine |
| R5/R6 — équipements et période du festival | `validate_concert_assignment` |
| R7 — planning publié non modifiable | État `FestivalStatus` et garde `ensure_schedule_is_editable()` avant programmation, déplacement ou annulation |
| R8 — planning valide avant publication | `PublicationService` charge le planning, appelle `validate_full_schedule`, puis applique la transition |
| R9 — capacité et créneau valides | `validate_capacity` et `TimeSlot` |
| R10 — incident relié à un concert, description non vide | `IncidentService`, qui consulte le port de concerts et valide la description |

La répartition complète, les tests de référence et les limites de chaque garantie sont recensés dans [regles-metier.md](./regles-metier.md).

## Corrections des défauts initiaux

1. **Chevauchements lors d'un déplacement** : les concerts actifs sont récupérés via les ports et comparés par les règles du domaine. Le concert déplacé est exclu de sa propre comparaison.
2. **Échec de notification après déplacement** : le cas d'utilisation persiste d'abord le nouveau créneau, puis tente la notification. Un échec connu est journalisé; la réponse demeure HTTP 200 avec `X-Notification-Status: failed`, car le changement est déjà enregistré.
3. **Modification après publication** : les créations, déplacements et annulations ordinaires appellent la garde métier du festival et sont refusés quand l'état est `PUBLISHED`.

## Tests et validation

La suite est organisée en tests du domaine sans base, tests des cas d'utilisation avec repositories en mémoire, et tests des routes et adaptateurs de persistance. Les tests de non-régression couvrent les défauts reproduits.

Dernière validation associée à cette note : `pytest` passe avec **49 tests réussis** après l'ajout des tests de transitions d'état. Le test de démarrage HTTP de l'API renvoie également `200`. Des avertissements de dépréciation tiers concernant Starlette et `datetime.utcnow()` restent non bloquants.

## Compromis et limites restantes

- Les entités métier sont séparées des modèles ORM, mais les frontières d'agrégats Festival/Planning/Concert ne sont pas encore matérialisées comme objets cohérents complets.
- La liste des concerts est chargée pour détecter les conflits; une stratégie de concurrence (verrouillage ou contrôle optimiste) n'est pas implémentée.
- La notification est synchrone et sans outbox/reprise automatique. L'échec après publication du festival n'a pas encore le même résultat explicite que celui du déplacement : l'état est commité avant l'envoi et l'erreur peut remonter en HTTP 500.
- L'état du concert (`scheduled`/`cancelled`) reste une chaîne; seule la transition de l'état du planning est typée dans cette tranche.
- Les règles ne protègent pas contre une modification directe de la base par un outil externe; la validation complète à la publication aide à détecter une partie de ces incohérences.
- Les étapes de lancement sont documentées dans le [README](../../README.md). La checklist de rendu consigne une vérification depuis un environnement virtuel Python 3.13 propre, avec `pip check`, les 49 tests et des vérifications HTTP de l'API.

## Diagrammes

- [Diagramme de composants PlantUML](./diagramme-composants.puml) ([SVG](./diagramme-composants.svg))
- [Diagramme de séquence PlantUML](./diagramme-sequence-deplacement.puml) ([SVG](./diagramme-sequence-deplacement.svg))

## Références détaillées

- [Diagnostic initial](./diagnostic-initial.md)
- [Modélisation métier](./modele-metier.md)
- [Règles métier R1–R10](./regles-metier.md)
- [README et procédures d'exécution](../../README.md)
