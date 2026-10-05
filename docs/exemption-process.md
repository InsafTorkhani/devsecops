# Processus d’exemption de faux positif

## 1. Principe

Une exemption ne doit être utilisée qu’en cas de faux positif justifié.

## 2. Règles

- documenter la justification ;
- attribuer un propriétaire ;
- fixer une date d’expiration ;
- valider dans une merge request ;
- conserver une trace en historique.

## 3. Exemple

Un scan détecte un secret dans un fichier de test qui n’est pas exploitable.

## 4. Vérification

La règle doit être revisée régulièrement et supprimée dès que la vraie cause est traitée.
