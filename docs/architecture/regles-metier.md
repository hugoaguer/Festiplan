# Règles métier FestiPlan (R1–R10)

Ce fichier est le point d'entrée pour retrouver les règles métier, leurs protections et les tests qui les verrouillent. Les règles de planning réutilisables sont centralisées dans `app/domain/scheduling.py`; les cas d'utilisation les appellent via des entités métier indépendantes, et les adaptateurs HTTP traduisent les erreurs en réponses HTTP.

## Tableau de suivi

| Réf. | Règle | Protection principale | Tests de référence |
| --- | --- | --- | --- |
| R1 | La fin du concert est strictement après le début | `TimeSlot.__post_init__` | `tests/test_domain_scheduling.py::test_time_slot_requires_end_after_start`; `tests/test_concerts_api.py` |
| R2 | Pas de chevauchement sur une scène | `ensure_no_conflicts` | `tests/test_domain_scheduling.py::test_conflicts_reject_shared_stage_or_artist`; `tests/test_scheduling.py::test_reschedule_rejects_overlap_on_same_stage` |
| R3 | Un artiste ne joue pas simultanément sur plusieurs scènes ou festivals | `ensure_no_conflicts` sur tous les concerts actifs | `tests/test_scheduling.py::test_reschedule_rejects_artist_overlap_across_stages`; `test_reschedule_rejects_artist_overlap_across_festivals` |
| R4 | Références Festival/Artiste/Scène existantes; scène rattachée au bon festival | Chargement des références dans `SchedulingService`; `validate_concert_assignment`; vérification des références à la publication | `tests/test_scheduling.py::test_create_concert_rejects_missing_references`; `test_create_concert_rejects_stage_from_another_festival`; `tests/test_domain_scheduling.py::test_assignment_requires_stage_from_same_festival` |
| R5 | Équipements requis présents sur la scène | `equipment_set` et `validate_concert_assignment` | `tests/test_scheduling.py::test_create_concert_requires_artist_equipment_on_stage`; `tests/test_domain_scheduling.py::test_assignment_requires_all_artist_equipment` |
| R6 | Concert entièrement dans la période du festival | `validate_concert_assignment` | `tests/test_scheduling.py::test_create_concert_must_fit_festival_period`; `tests/test_domain_scheduling.py::test_assignment_must_fit_festival_period` |
| R7 | Planning publié protégé contre les opérations ordinaires | `FestivalStatus` et `Festival.ensure_schedule_is_editable`, appelés par `SchedulingService` | Tests de publication et de modification après publication dans `tests/test_scheduling.py`; tests de transition dans `tests/test_domain_scheduling.py` |
| R8 | Tout le planning est valide avant publication | `validate_full_schedule` appelé par `PublicationService.publish` | `tests/test_publication.py::test_publish_rejects_invalid_schedule_and_keeps_preparation_status`; tests unitaires de politique dans `tests/test_domain_scheduling.py` |
| R9 | Capacité et durées/quantités obligatoires strictement positives | `validate_capacity`; `TimeSlot` pour les durées | `tests/test_stages_api.py`; `tests/test_domain_scheduling.py::test_capacity_must_be_positive`; `test_time_slot_requires_end_after_start` |
| R10 | Incident lié à un concert existant, description non vide | `IncidentService` vérifie le concert via le port de lecture; `validate_incident_description` valide le texte | `tests/test_incidents_api.py`; `tests/test_domain_scheduling.py::test_incident_description_must_not_be_blank`; `tests/test_application_services.py` |

## Où modifier les règles

- Modifier une règle de créneau, de disponibilité, d'équipement, de période, de capacité ou de description dans `app/domain/scheduling.py`.
- Les opérations qui lisent des données persistées (références et sélection des concerts) sont orchestrées par `app/services/scheduling_service.py` ou `app/services/publication_service.py`, via les ports de `app/ports.py`.
- Le cas incident est orchestré par `app/services/incident_service.py`; la route HTTP ne fait que convertir la requête/réponse.
- Ajouter ou adapter le test du domaine dans `tests/test_domain_scheduling.py`, puis le test du parcours HTTP concerné. Les tests d'API assurent que les règles sont également respectées depuis l'interface publique.

## Comportement de publication

La validation ignore les concerts annulés et vérifie les références disponibles, l'appartenance festival/scène, le créneau, la période, les équipements et les conflits avant de passer l'état du festival à `published`. Si une règle échoue, l'API renvoie HTTP 400 et le festival reste en préparation. Un festival sans concert est publiable.

Les invariants s'appliquent lors des opérations applicatives courantes. Une altération directe de la base par un outil externe peut contourner les services; la publication revalide tout le planning pour détecter ces incohérences avant de le rendre public.
