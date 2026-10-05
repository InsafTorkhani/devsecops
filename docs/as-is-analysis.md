# Analyse de l'état actuel (as-is)

## 1. Objectif

Documenter le pipeline initial avant l’ajout des contrôles de sécurité.

## 2. Pipeline actuel envisagé

```text
Code source -> build -> tests unitaires -> build image -> deployment staging
```

## 3. Faiblesses identifiées

- absence de scan de secrets
- dépendances non vérifiées
- image Docker non scannée
- pas de contrôle DAST
- pas de quality gate de sécurité

## 4. Éléments à compléter

- schéma détaillé
- outils présents
- points faibles
- comparaison avec l’état cible
