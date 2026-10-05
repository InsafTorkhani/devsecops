# DevSecOps Project

Ce projet vise à construire une pipeline CI/CD sécurisée avec GitLab CI, Docker et un runner local.

## Structure

- `app.py` : application Flask de démonstration
- `requirements.txt` : dépendances Python
- `Dockerfile` : image Docker
- `.gitlab-ci.yml` : pipeline initiale
- `tests/test_app.py` : test unitaire de base
- `docs/` : documentation du projet

## Étapes suivantes

1. installer Python localement
2. installer les dépendances
3. exécuter le test
4. activer les scanners de sécurité
5. ajouter les quality gates

## Commandes utiles

```bash
python -m pip install -r requirements.txt
pytest -q
python app.py
```
