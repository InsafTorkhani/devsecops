# DevSecOps Project – Plan de travail et exigences

## 1. Objectif global

Ce projet a pour but de construire une pipeline CI/CD sécurisée pour une petite application web, en intégrant les contrôles de sécurité à chaque étape du cycle de vie : développement, validation, packaging, déploiement et test en environnement de staging.

L’objectif principal n’est pas seulement d’installer des outils, mais de comprendre :

- pourquoi chaque scan existe ;
- quel type de vulnérabilité il détecte ;
- quels seuils de blocage sont pertinents ;
- pourquoi le pipeline doit arrêter le build en cas de vulnérabilités critiques ou élevées.

Le projet est réalisé avec :

- GitLab CI
- Docker
- un PC personnel comme GitLab Runner
- une application Python Flask simple (créée pour la démonstration)

---

## 2. Ce que le professeur attend

Les exigences suivantes doivent être couvertes, ou bien volontairement laissées de côté et justifiées.

### 2.1 Objectifs pédagogiques

- Comprendre le concept de DevSecOps et le principe de “shift-left security”
- Intégrer SAST, SCA, DAST, secret scan et image scan dans une vraie pipeline
- Définir des quality gates qui bloquent la construction si des vulnérabilités critiques sont détectées
- Produire une documentation claire et reproductible, exploitable par une autre équipe

### 2.2 Analyse du pipeline existant (as-is)

- Cartographier le pipeline actuel : build, tests, packaging, déploiement
- Identifier les outils déjà en place (ici : GitLab CI)
- Repérer les faiblesses de sécurité : secrets en clair, dépendances non vérifiées, images Docker non scannées, absence de contrôle de sécurité
- Documenter l’état initial pour comparer avec l’état cible

### 2.3 Côté développeur (shift-left)

- Sécuriser l’environnement IDE (VS Code) avec des extensions de sécurité
- Ajouter du linting local / SAST : Bandit, Semgrep
- Mettre en place des hooks pre-commit pour bloquer un commit contenant un secret ou un défaut évident
- Détecter des mauvais patterns tels que : XSS, injection SQL, désérialisation insecure, secrets exposés, dépendances vulnérables
- Corriger immédiatement les problèmes avant commit/push
- Documenter les références OWASP Top 10 et OWASP ASVS

### 2.4 Contrôles automatisés dans la pipeline

Les contrôles doivent être intégrés dans des stages nommés clairement :

- secrets_scan
- sast
- scan_dependencies
- docker_scan
- dast

Contrôles attendus :

- Secrets scan : détecter clés, tokens, mots de passe dans le code → Gitleaks
- SAST : détecter des vulnérabilités dans le code → Semgrep et Bandit
- SCA : analyser les dépendances pour détecter des vulnérabilités → Trivy (filesystem mode)
- Docker image scan : analyser l’image Docker et son image de base → Trivy (image mode)
- DAST : attaquer l’application en environnement de staging → OWASP ZAP
- IaC scan (optionnel) : vérifier Dockerfile / Terraform / Kubernetes → Trivy config ou Checkov
- SBOM (optionnel) : générer un inventaire de composants pour traçabilité et conformité → Syft / CycloneDX

### 2.5 Intégration technique dans la pipeline

- Fichier GitLab CI : `.gitlab-ci.yml`
- Stages distincts et nommés
- Quality gates basés sur la gravité (CVSS)
- Blocage automatique sur vulnérabilités critiques ou hautes
- Contrôles bloquants vs non bloquants
- Gestion sécurisée des secrets via variables CI protégées et masquées
- Exécution sur chaque push et merge request, avec exécution locale avant push

### 2.6 Reporting et alerting

- Rapport HTML et/ou JSON pour chaque scan
- Sauvegarde des artefacts dans GitLab
- Notification sur échec via mail, Slack ou Teams
- Historisation des résultats pour suivre l’évolution dans le temps

### 2.7 Documentation et sensibilisation

- Rédiger un rapport de projet : démarche, outils, intégration, résultats et difficultés
- Produire un schéma avant/après du pipeline
- Expliquer le processus d’exemption en cas de faux positif
- Automatiser l’exécution des tests de sécurité à chaque push/MR

### 2.8 Livrables attendus

- Pipeline CI/CD fonctionnelle
- Fichier `.gitlab-ci.yml` versionné et commenté
- Rapport de projet
- Captures d’écran / exports des rapports d’outils
- Support de présentation orale

### 2.9 Critères d’évaluation

Le travail sera évalué sur :

1. Qualité de l’analyse du pipeline existant
2. Cohérence et qualité de l’intégration des outils
3. Pertinence des seuils de blocage et justification
4. Clarté du rapport et des captures
5. Compréhension réelle des enjeux DevSecOps et non seulement la mise en œuvre technique

---

## 3. Décisions clés déjà prises

- Système CI : GitLab CI
- Runner : PC personnel avec Docker executor
- Application : petite app Flask Python avec vulnérabilités intentionnelles pour valider le pipeline
- Mode de travail : solo, avec adaptation du scope selon le planning

---

## 4. Exemple d’application cible

L’application ne sera pas forcément une application réelle existante ; elle peut être créée comme un mini projet de démonstration avec des vulnérabilités intentionnelles.

Ces vulnérabilités servent à prouver que les outils fonctionnent réellement.

Exemples de défauts à prévoir :

- secret codé en dur dans le code
- injection SQL via concaténation de chaînes
- usage d’unsafe `yaml.load`
- `debug=True` dans Flask
- dépendances anciennes et vulnérables
- image Docker basée sur `python:3.8` avec utilisation de root
- absence de headers de sécurité sur l’application

Ces défauts doivent être détectés par :

- Gitleaks
- Semgrep / Bandit
- Trivy
- ZAP

---

## 5. Politique de qualité et seuils bloquants

La politique suivante est proposée et devra être justifiée dans le rapport.

### Seuils recommandés

- Critical : 9.0 à 10.0
- High : 7.0 à 8.9
- Medium : 4.0 à 6.9
- Low : moins de 4.0

### Règle de blocage proposée

| Stage | Blocage | Non bloquant |
| --- | --- | --- |
| secrets_scan | Toute secret trouvé | — |
| sast | Severity ERROR / High critical logic | Warning / Info |
| scan_dependencies | Critique ou élevée (avec correctif disponible) | Medium / Low |
| docker_scan | Critique ou élevée | Medium / Low |
| dast | High alerts | Medium / Low / info |

### Processus d’exemption

En cas de faux positif bloquant, il faut documenter :

- un fichier d’exclusion (`.gitleaksignore`, `.trivyignore`, ou règle Semgrep `nosemgrep`)
- une justification écrite
- un propriétaire responsable
- une date d’expiration
- une revue dans une merge request

---

## 6. Pipeline cible (to-be)

```text
Developer PC                  GitLab CI (runner sur mon PC)
─────────────────          ─────────────────────────────────────────────
pre-commit hooks         push   build → test → secrets_scan → sast →
(gitleaks, semgrep,           → scan_dependencies → docker_build → docker_scan →
 bandit)                      deploy_staging → dast → notify

Quality gates : fail on Critical / High
Reports saved as artifacts
```

---

## 7. Plan de travail par phases

### Phase 0 – Préparation de l’environnement (0,5 jour)

Objectif : mettre en place le socle technique.

À faire :

- installer Git, Docker Desktop, VS Code et Python
- créer le projet GitLab vide et le cloner localement
- installer et enregistrer le GitLab Runner sur le PC personnel
- tester un pipeline simple “hello world” sur le runner

À comprendre :

- la différence entre CI/CD
- rôle du runner
- rôle de l’executor Docker
- intérêt du Docker dans un runner CI

### Phase 1 – Analyse de l’état actuel et création de la base (0,5 jour)

Objectif : partir d’une base technique minimale mais fonctionnelle.

À faire :

- créer une petite app Flask avec vulnérabilités intentionnelles
- créer des tests unitaires
- créer un `Dockerfile`
- écrire une pipeline de base : build, test, docker_build
- faire l’analyse “as-is” : diagramme, outils existants, faiblesses de sécurité

Livrables attendus :

- schéma du pipeline actuel
- description des faiblesses
- base applicative et base CI

### Phase 2 – Shift-left côté développeur (0,5 jour)

Objectif : détecter les problèmes avant même de pousser le code.

À faire :

- installer Semgrep, Bandit et éventuellement SonarLint
- installer `pre-commit`
- configurer les hooks Gitleaks, Semgrep et Bandit
- tester le blocage d’un secret ou d’un défaut obvious
- documenter le lien avec OWASP Top 10 / ASVS

À améliorer :

- réduction des coûts de correction
- prévention de la fuite de secrets
- prévention de vulnérabilités avant le merge

### Phase 3 – Stages de sécurité dans la pipeline (1 jour)

Objectif : intégrer les scans automatiques dans GitLab CI.

À faire :

- secrets_scan avec Gitleaks
- sast avec Semgrep
- scan_dependencies avec Trivy
- docker_scan avec Trivy sur l’image construite
- dast : lancer l’application en staging puis scanner avec OWASP ZAP
- enregistrer les rapports HTML / JSON comme artefacts

Concept à maîtriser :

- ce que chaque outil voit ;
- ce qu’il ne voit pas ;
- pourquoi les outils sont complémentaires et non redondants.

### Phase 4 – Quality gates et gestion des secrets (0,5 jour)

Objectif : transformer les scans en vraie barrière de sécurité.

À faire :

- définir les règles de sortie (exit codes)
- utiliser `allow_failure` pour les contrôles non bloquants
- stocker les secrets dans les variables CI protégées et masquées
- documenter le processus d’exemption et les faux positifs
- faire une démonstration d’un cas de faux positif documenté

### Phase 5 – Reporting et alerting (0,5 jour)

Objectif : rendre les résultats exploitables et visibles.

À faire :

- centraliser les rapports GitLab artefacts
- définir une stratégie de notification
- conserver les résultats pour suivre l’évolution dans le temps
- préparer les captures d’écran pour le rapport

### Phase 6 – Démo, rapport et soutenance (1 jour)

Objectif : finaliser la preuve de fonctionnement et la documentation.

À faire :

- faire une démonstration complète : version vulnérable bloquée, correctif, pipeline verte
- capturer les écrans et exportations
- rédiger le rapport final
- préparer une présentation orale concise

---

## 8. Planning temporel (4 jours)

| Jour | Phase(s) | Objectif |
| --- | --- | --- |
| Jour 1 | Phase 0 + 1 + 2 | Setup, app, pipeline de base, hooks locals |
| Jour 2 | Phase 3 | Intégration des scanners et rapports |
| Jour 3 | Phase 4 + 5 | Quality gates, secrets, notification |
| Jour 4 | Phase 6 | Démo, rapport, soutenance |

### Si le temps manque

Couper dans l’ordre suivant :

1. Stretch goals (IaC, SBOM, dashboards)
2. Partie historique / reporting avancé
3. SonarLint

Ne jamais couper :

- qualité gate
- exemption process
- rapport final

---

## 9. Risques et précautions

| Risque | Mitigation |
| --- | --- |
| Runner PC ne peut pas construire les images Docker | utiliser le Docker executor et bind le socket Docker |
| DAST nécessite une application active dans le pipeline | la lancer en service container dans le stage staging |
| Trop de vulnérabilités, pipeline toujours rouge | commencer avec seuils critiques / élevées seulement |
| Téléchargements lents ou bloqués | utiliser des images officielles et tester les pulls tôt |
| Manque de temps | respecter le plan de coupure ci-dessus |

---

## 10. Cadre de travail “teacher mode”

Pour chaque phase, la méthode à suivre est :

1. expliquer le concept en français simple avec une analogie
2. vérifier la compréhension avec quelques questions rapides
3. implémenter seulement quand le point est validé
4. vérifier que cela fonctionne réellement
5. noter dans le rapport les éléments à montrer (capture d’écran, finding, décision)

---

## 11. Structure de projet cible

```text
devsecops-project/
├── app.py
├── requirements.txt
├── Dockerfile
├── tests/
│   └── test_app.py
├── .gitlab-ci.yml
├── .pre-commit-config.yaml
├── .gitleaksignore
├── .trivyignore
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── as-is-analysis.md
│   ├── exemption-process.md
│   └── report/
│       └── screenshots/
├── README.md
└── .gitignore
```

---

## 12. Première liste de tâches à exécuter

### À faire immédiatement

- [ ] créer le dossier project et la structure de base
- [ ] créer le dossier `docs/`
- [ ] rédiger le plan de travail dans ce document
- [ ] préparer l’environnement local : Git, Python, Docker, VS Code
- [ ] initialiser un dépôt GitLab et un runner local
- [ ] créer une app Flask simple de test
- [ ] écrire une première version de `.gitlab-ci.yml` basique
- [ ] ajouter les premiers hooks `pre-commit`
- [ ] valider le flux de build / test / scan

### À faire ensuite

- [ ] intégrer Gitleaks
- [ ] intégrer Semgrep / Bandit
- [ ] intégrer Trivy pour les dépendances
- [ ] intégrer Trivy pour l’image Docker
- [ ] intégrer OWASP ZAP en staging
- [ ] écrire le rapport final
- [ ] préparer la présentation orale

---

## 13. Plan de démarrage concret

Pour commencer sans se perdre :

1. Créer la structure de projet
2. Définir le mini projet Flask avec une vulnérabilité volontaire
3. Créer les tests de base
4. Créer le Dockerfile
5. Créer une pipeline GitLab simple de build + test
6. Ajouter progressivement les scanners : secret, SAST, dépendances, image, DAST
7. Définir les seuils de blocage
8. Vérifier le fonctionnement sur le runner local
9. Rédiger le rapport et les preuves

---

## 14. Note importante

Ce document est la base du projet. Il doit être enrichi au fur et à mesure avec :

- les captures d’écran
- les résultats obtenus
- les erreurs rencontrées et leurs corrections
- les décisions de qualité gate
- les justifications de configuration

---

## 15. Prochaine étape recommandée

La prochaine étape logique est de créer le squelette du projet et de démarrer par :

- le dossier `docs/`
- le fichier de plan
- puis la base application Flask + fichier Docker + pipeline GitLab de base

Cela permettra de construire la suite de manière structurée et de respecter le plan décrit dans le mail du professeur.
