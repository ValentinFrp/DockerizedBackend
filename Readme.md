# 🚀 User Management API - FastAPI avec CI/CD

[![CI/CD Pipeline](https://github.com/your-username/DockerizedBackend/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/DockerizedBackend/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 Table des matières

- [Présentation](#-présentation)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Installation locale](#-installation-locale)
- [Exécution](#-exécution)
- [Tests](#-tests)
- [Pipeline CI/CD](#-pipeline-cicd)
- [Docker](#-docker)
- [API Documentation](#-api-documentation)
- [Structure du projet](#-structure-du-projet)
- [Choix techniques](#-choix-techniques)
- [Contribution](#-contribution)

---

## 🎯 Présentation

Ce projet est une **API REST de gestion d'utilisateurs** développée avec FastAPI, démontrant les meilleures pratiques DevOps :

✅ **Backend moderne** : FastAPI avec validation Pydantic  
✅ **Tests complets** : Pytest avec couverture de code  
✅ **Qualité de code** : Black + Flake8 + isort  
✅ **Conteneurisation** : Dockerfile multi-stage optimisé  
✅ **CI/CD automatisé** : GitHub Actions  
✅ **Prêt pour la production** : Health checks, logging, sécurité

---

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   GitHub Push   │─────▶│  GitHub Actions  │─────▶│   Docker Hub    │
│                 │      │   CI/CD Pipeline │      │  Image Registry │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
               ┌─────────┐   ┌─────────┐   ┌─────────┐
               │  Lint   │   │  Test   │   │  Build  │
               │ (Black) │   │ (Pytest)│   │ (Docker)│
               └─────────┘   └─────────┘   └─────────┘
```

### Pipeline CI/CD

1. **Linting** : Vérification du formatage (Black, isort) et du code (Flake8)
2. **Tests** : Exécution des tests unitaires avec couverture
3. **Build** : Construction de l'image Docker multi-stage
4. **Push** : Déploiement automatique sur Docker Hub (branche main uniquement)
5. **Security** : Scan de vulnérabilités avec Trivy

---

## ⚙️ Prérequis

- **Python** 3.11+
- **Docker** 20.10+
- **Docker Compose** 2.0+ (optionnel)
- **Make** (optionnel, pour les commandes simplifiées)
- **Git**

---

## 📦 Installation locale

### 1. Cloner le repository

```bash
git clone https://github.com/your-username/DockerizedBackend.git
cd DockerizedBackend
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Ou avec Make :**
```bash
make install
```

---

## 🚀 Exécution

### Méthode 1 : Exécution directe avec Python

```bash
# Mode développement avec hot-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Ou avec Make
make run
```

### Méthode 2 : Avec Docker

```bash
# Construire l'image
docker build -t user-management-api .

# Lancer le conteneur
docker run -d -p 8000:8000 --name api user-management-api

# Ou avec Make
make docker-build
make docker-run
```

### Méthode 3 : Avec Docker Compose

```bash
docker-compose up -d

# Ou avec Make
make docker-compose-up
```

### Accéder à l'API

- **API** : http://localhost:8000
- **Documentation interactive** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Health check** : http://localhost:8000/health

---

## 🧪 Tests

### Exécuter tous les tests

```bash
pytest tests/ -v
```

### Tests avec couverture de code

```bash
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
```

**Ou avec Make :**
```bash
make test          # Tests simples
make test-cov      # Tests avec couverture
make check         # Lint + format + tests
```

### Structure des tests

- ✅ **Tests unitaires** : Chaque endpoint de l'API
- ✅ **Tests d'intégration** : Workflow CRUD complet
- ✅ **Tests de validation** : Vérification des contraintes Pydantic
- ✅ **Tests d'erreur** : Gestion des cas limites

**Couverture actuelle : >95%**

---

## 🔄 Pipeline CI/CD

Le pipeline GitHub Actions s'exécute automatiquement sur :
- **Push** vers `main` ou `develop`
- **Pull requests** vers `main`

### Étapes du pipeline

#### 1️⃣ **Code Quality Check** (Linting)
```yaml
- Black : Vérification du formatage
- isort : Vérification des imports
- Flake8 : Linting du code
```

#### 2️⃣ **Run Tests**
```yaml
- Exécution de tous les tests
- Génération du rapport de couverture
- Upload sur Codecov (optionnel)
```

#### 3️⃣ **Build Docker Image**
```yaml
- Construction de l'image Docker
- Test de l'image (health check)
- Cache pour accélérer les builds
```

#### 4️⃣ **Push to Docker Registry** (main uniquement)
```yaml
- Push automatique sur Docker Hub
- Tags : latest + SHA du commit
```

#### 5️⃣ **Security Scan**
```yaml
- Scan de vulnérabilités avec Trivy
- Upload des résultats sur GitHub Security
```

### Configuration requise

**Secrets GitHub à configurer :**
```bash
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-token
```

**Configuration du workflow :**
1. Aller dans `Settings` → `Secrets and variables` → `Actions`
2. Ajouter les secrets `DOCKER_USERNAME` et `DOCKER_PASSWORD`
3. Modifier `DOCKER_IMAGE_NAME` dans `.github/workflows/ci.yml`

### Simuler le pipeline localement

```bash
make ci-local
```

---

## 🐳 Docker

### Dockerfile multi-stage expliqué

```dockerfile
# Stage 1: Builder - Installation des dépendances
FROM python:3.11-slim as builder
# Création d'un environnement virtuel isolé
# Installation optimisée des dépendances

# Stage 2: Runtime - Image finale légère
FROM python:3.11-slim
# Copie uniquement de l'environnement virtuel
# Utilisateur non-root pour la sécurité
# Health check intégré
```

### Avantages du multi-stage :
- ✅ **Image finale légère** : ~150 MB (vs ~400 MB sans multi-stage)
- ✅ **Sécurité renforcée** : Utilisateur non-root
- ✅ **Cache optimisé** : Dépendances séparées du code
- ✅ **Health check** : Monitoring automatique

### Commandes Docker utiles

```bash
# Construire
make docker-build

# Lancer
make docker-run

# Voir les logs
make docker-logs

# Arrêter
make docker-stop

# Nettoyer
make docker-clean
```

---

## 📚 API Documentation

### Endpoints disponibles

#### 🏠 **Root**
```http
GET /
```
Message de bienvenue

#### ❤️ **Health Check**
```http
GET /health
```
Retourne le statut de l'API

#### 👤 **Créer un utilisateur**
```http
POST /users
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "securepassword123"
}
```

#### 📋 **Lister les utilisateurs**
```http
GET /users?skip=0&limit=100
```

#### 🔍 **Récupérer un utilisateur**
```http
GET /users/{user_id}
```

#### ✏️ **Mettre à jour un utilisateur**
```http
PUT /users/{user_id}
Content-Type: application/json

{
  "username": "johndoe_updated",
  "email": "john.updated@example.com",
  "full_name": "John Doe Updated"
}
```

#### 🗑️ **Supprimer un utilisateur**
```http
DELETE /users/{user_id}
```

### Exemples avec curl

```bash
# Health check
curl http://localhost:8000/health

# Créer un utilisateur
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Lister les utilisateurs
curl http://localhost:8000/users

# Récupérer un utilisateur
curl http://localhost:8000/users/1
```

---

## 📂 Structure du projet

```
DockerizedBackend/
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline CI/CD GitHub Actions
├── src/
│   ├── __init__.py
│   └── main.py                 # Application FastAPI principale
├── tests/
│   ├── __init__.py
│   └── test_main.py            # Tests unitaires complets
├── .dockerignore               # Exclusions pour Docker
├── .gitignore                  # Exclusions Git
├── docker-compose.yml          # Orchestration Docker
├── Dockerfile                  # Image Docker multi-stage
├── Makefile                    # Commandes simplifiées
├── pyproject.toml              # Configuration Black, isort, pytest
├── pytest.ini                  # Configuration Pytest
├── requirements.txt            # Dépendances Python
└── README.md                   # Cette documentation
```

---

## 💡 Choix techniques

### Pourquoi FastAPI ?
- ⚡ **Performance** : Basé sur Starlette et Pydantic, très rapide
- 📝 **Documentation auto** : OpenAPI/Swagger intégré
- ✅ **Validation** : Validation automatique avec Pydantic
- 🔄 **Async** : Support natif de l'asynchrone
- 🐍 **Type hints** : Utilisation complète des types Python

### Pourquoi Black + Flake8 + isort ?

#### Black (Formatage automatique)
- ✅ Formatage déterministe et cohérent
- ✅ Pas de débat sur le style de code
- ✅ Intégration facile avec les IDE

#### Flake8 (Linting)
- ✅ Détection des erreurs de code
- ✅ Respect des conventions PEP 8
- ✅ Détection de complexité excessive

#### isort (Organisation des imports)
- ✅ Tri automatique des imports
- ✅ Séparation claire (stdlib, third-party, local)
- ✅ Compatible avec Black

### Pourquoi Pytest ?
- ✅ **Syntaxe simple** : Plus pythonique que unittest
- ✅ **Fixtures puissantes** : Réutilisation facile
- ✅ **Plugins riches** : pytest-cov, pytest-asyncio, etc.
- ✅ **Rapports détaillés** : Output clair et informatif

### Pourquoi Docker multi-stage ?
- 🔒 **Sécurité** : Image minimale = surface d'attaque réduite
- 📦 **Taille** : Image finale 3x plus petite
- ⚡ **Performance** : Cache Docker optimisé
- 🔧 **Maintenabilité** : Séparation build/runtime

### Pourquoi GitHub Actions ?
- 🆓 **Gratuit** : Pour les projets open source
- 🔗 **Intégré** : Native sur GitHub
- 🔌 **Extensible** : Marketplace d'actions riche
- 🚀 **Rapide** : Exécution parallèle des jobs

---

## 🛠️ Commandes Make disponibles

```bash
make help              # Afficher toutes les commandes
make install           # Installer les dépendances
make test              # Exécuter les tests
make test-cov          # Tests avec couverture
make lint              # Vérifier le code
make format            # Formatter le code
make check             # Tout vérifier (lint + format + tests)
make run               # Lancer l'API localement
make docker-build      # Construire l'image Docker
make docker-run        # Lancer le conteneur
make docker-stop       # Arrêter le conteneur
make clean             # Nettoyer les fichiers temporaires
make ci-local          # Simuler le pipeline CI
```

---

## 🤝 Contribution

### Workflow de contribution

1. **Fork** le projet
2. **Créer** une branche (`git checkout -b feature/AmazingFeature`)
3. **Commit** les changements (`git commit -m 'Add AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

### Standards de code

Avant de soumettre :
```bash
make format  # Formatter le code
make check   # Vérifier tout
```

Le pipeline CI vérifiera automatiquement :
- ✅ Formatage (Black)
- ✅ Imports (isort)
- ✅ Linting (Flake8)
- ✅ Tests (Pytest)
- ✅ Couverture de code (>80%)

---

## 📈 Améliorations futures

### Fonctionnalités
- [ ] Authentification JWT
- [ ] Base de données PostgreSQL
- [ ] Migrations avec Alembic
- [ ] Rate limiting
- [ ] Caching avec Redis
- [ ] WebSockets

### DevOps
- [ ] Déploiement Kubernetes
- [ ] Monitoring avec Prometheus/Grafana
- [ ] Logs centralisés (ELK Stack)
- [ ] Load testing avec Locust
- [ ] Déploiement multi-environnements

---

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👨‍💻 Auteur

**DevOps Team**
- Email: valentinn.frappart@gmail.com

---

## 🙏 Remerciements

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderne
- [Docker](https://www.docker.com/) - Conteneurisation
- [GitHub Actions](https://github.com/features/actions) - CI/CD
- [Pytest](https://pytest.org/) - Framework de test

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Consultez la [documentation](http://localhost:8000/docs)
2. Ouvrez une [issue](https://github.com/your-username/DockerizedBackend/issues)
3. Rejoignez les [discussions](https://github.com/your-username/DockerizedBackend/discussions)

---

**⭐ Si ce projet vous a aidé, n'hésitez pas à lui donner une étoile !**
