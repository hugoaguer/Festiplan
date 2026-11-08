# Diagnostic de l'architecture initiale

## Périmètre et état de référence

FestiPlan est un monolithe FastAPI : les fonctionnalités tournent dans un seul processus et partagent une base SQLAlchemy. Ce choix n'est pas un défaut en soi. Le problème initial est le couplage entre transport HTTP, règles métier, accès aux données et effets secondaires.

Avant la première tranche de refactorisation, la suite existante passait : **6 tests réussis**, avec un avertissement de dépréciation provenant de `starlette.testclient`. Les tests initiaux couvraient peu les règles de programmation.

## Endpoints observés

| Domaine | Endpoints |
| --- | --- |
| Santé | `GET /` |
| Festivals | `GET /festivals`, `POST /festivals`, `POST /festivals/{festival_id}/publish` |
| Artistes | `GET /artists`, `POST /artists` |
| Scènes | `GET /stages?festival_id=...`, `POST /stages` |
| Concerts | `GET /concerts?festival_id=...`, `GET /concerts/{concert_id}`, `POST /concerts`, `PATCH /concerts/{concert_id}/reschedule`, `POST /concerts/{concert_id}/cancel`, `GET /concerts/schedule/{festival_id}` |
| Incidents | `GET /incidents?concert_id=...`, `POST /incidents` |

## Responsabilités et dépendances constatées

- `app/api/` expose les routes, construit les réponses HTTP et traduit certaines erreurs en codes HTTP.
- `app/schemas.py` définit les entrées et sorties Pydantic, donc les contrats de transport et certaines validations de forme.
- `app/services/` orchestre les opérations, mais contient aussi des règles métier et utilise directement `Session` SQLAlchemy.
- `app/repositories/` exécute des requêtes SQLAlchemy; les repositories effectuent également des commits, ce qui mêle persistance et décision transactionnelle.
- `app/models.py` définit les modèles ORM et leurs relations; les objets persistés sont utilisés directement dans les services et les réponses HTTP.
- `app/database.py` crée le moteur, la session et la base déclarative. `app/main.py` assemble l'application et crée les tables au démarrage.
- Les notifications sont déclenchées depuis les services et aboutissent à `app/utils/email_sender.py`, qui dépend des paramètres globaux.

Le chemin nominal est donc souvent `route FastAPI -> service -> repository -> SQLAlchemy`. Cependant, ce chemin n'est pas systématique : plusieurs routes interrogent la session directement. Le service de programmation est lui-même dépendant de SQLAlchemy et de l'envoi de notification.

## Exemples de responsabilités mal placées

- Dans `app/api/concerts.py`, la lecture d'un concert et, initialement, la recherche préalable avant déplacement interrogeaient directement SQLAlchemy depuis le contrôleur HTTP. Le contrôleur connaissait donc le schéma de persistance.
- Dans `app/api/incidents.py`, la route vérifie l'existence du concert, instancie le modèle ORM, ajoute l'incident et valide la transaction. La route cumule adaptation HTTP, règle de référence et persistance.
- Dans `app/services/scheduling_service.py`, les règles de disponibilité, les accès SQLAlchemy et l'envoi de notification étaient regroupés. Il était donc difficile de tester la décision métier sans base de données et de maîtriser séparément la transaction et l'effet secondaire.

## Règles métier et risques initiaux

Les règles étaient dispersées entre schémas Pydantic, routes et services. Par exemple, la validation du créneau existait dans le parcours de création et dans le contrôleur de déplacement, mais le service de déplacement ne vérifiait pas les conflits, les équipements, la période du festival ou l'état publié. Appeler cette opération autrement que via son contrôleur pouvait donc contourner des vérifications HTTP.

Les services recevaient une session SQLAlchemy concrète plutôt qu'un contrat de persistance. Cela rendait les tests applicatifs dépendants de la base et compliquait le remplacement de l'adaptateur. Les commits réalisés dans les repositories ou directement dans les services rendaient également les frontières transactionnelles peu explicites.

## Reproduction des défauts initiaux

Les tests de non-régression ont été exécutés avant la correction de la première tranche :

1. **Chevauchements lors d'un déplacement** : le test de conflit sur la même scène attendait HTTP 400, mais obtenait HTTP 200. Le test de chevauchement du même artiste sur deux scènes obtenait également HTTP 200.
2. **Échec de notification après persistance** : avec `FESTIPLAN_FAIL_NOTIFICATIONS=true`, le déplacement était commité avant l'appel de notification. L'API retournait HTTP 500 alors que le nouveau créneau était enregistré.
3. **Modification après publication** : après publication, un déplacement ordinaire obtenait HTTP 200 au lieu d'être refusé.

Le test de déplacement valide réussissait, ce qui sert de contrôle pour préserver ce comportement lors de la correction.

## Première tranche réalisée

La première correction extrait `TimeSlot`, `ScheduledConcert` et la règle de conflit dans `app/domain/scheduling.py`. Le déplacement vérifie maintenant les conflits de scène et d'artiste (y compris entre festivals) ainsi que les règles de programmation déjà portées par le service. Les programmations, déplacements et annulations ordinaires sont refusés après publication.

Après validation et persistance d'un déplacement, un échec connu de notification est journalisé sans transformer la réponse en erreur HTTP trompeuse. La réponse porte `X-Notification-Status: failed` pour rendre l'échec secondaire visible. Cette première tranche ne constitue pas encore une architecture hexagonale complète : les services métier existants dépendent toujours directement de SQLAlchemy, et les autres parcours restent à refactoriser.

## Architecture après la migration hexagonale

La suite de la refactorisation a introduit les éléments suivants :

- `app/domain/entities.py` contient des entités de données indépendantes de SQLAlchemy.
- `app/application_ports.py` définit les contrats entrants des actions offertes par l'application.
- `app/ports.py` définit les contrats sortants de repositories et de notification.
- `app/services/` orchestre les cas d'utilisation en ne dépendant que du domaine et des ports.
- `app/adapters/sqlalchemy_repositories.py` convertit les modèles ORM en entités du domaine et assure la persistance.
- `app/adapters/notifications.py` adapte le faux expéditeur au port de notification.
- `app/api/` traduit HTTP et appelle les ports entrants; aucune route n'accède directement à SQLAlchemy.
- `app/composition.py` instancie les adaptateurs et les cas d'utilisation avec les dépendances concrètes.

Les services ne reçoivent plus de session et n'instancient plus de repositories ou de services techniques. Les cas d'utilisation sont testés avec des repositories en mémoire. Les règles métier restent protégées par les tests de domaine et d'intégration.
