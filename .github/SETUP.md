# 🔧 Configuration GitHub Actions - Guide de Setup

Ce guide explique comment configurer les secrets et variables nécessaires pour le pipeline CI/CD.

## 📋 Table des matières

- [Secrets requis](#secrets-requis)
- [Configuration Docker Hub](#configuration-docker-hub)
- [Configuration GitHub Container Registry](#configuration-github-container-registry-ghcr)
- [Variables d'environnement](#variables-denvironnement)
- [Vérification](#vérification)
- [Dépannage](#dépannage)

---

## 🔐 Secrets requis

Le pipeline CI/CD nécessite les secrets suivants pour fonctionner :

### 1. Docker Hub (Recommandé)

| Secret | Description | Exemple |
|--------|-------------|---------|
| `DOCKER_USERNAME` | Nom d'utilisateur Docker Hub | `john_doe` |
| `DOCKER_PASSWORD` | Token d'accès Docker Hub | `dckr_pat_xxxxx...` |

### 2. GitHub Container Registry (Alternative)

| Secret | Description | Exemple |
|--------|-------------|---------|
| `GHCR_TOKEN` | Personal Access Token GitHub | `ghp_xxxxx...` |

---

## 🐳 Configuration Docker Hub

### Étape 1 : Créer un compte Docker Hub

1. Allez sur [https://hub.docker.com](https://hub.docker.com)
2. Créez un compte gratuit (si vous n'en avez pas)
3. Vérifiez votre email

### Étape 2 : Créer un Access Token

1. Connectez-vous à Docker Hub
2. Cliquez sur votre nom d'utilisateur (en haut à droite) → **Account Settings**
3. Allez dans l'onglet **Security**
4. Cliquez sur **New Access Token**
5. Donnez-lui un nom descriptif : `github-actions-ci-cd`
6. Sélectionnez les permissions : **Read, Write, Delete**
7. Cliquez sur **Generate**
8. **⚠️ IMPORTANT** : Copiez le token immédiatement (vous ne pourrez plus le voir)

### Étape 3 : Créer un repository Docker Hub

1. Allez sur [https://hub.docker.com](https://hub.docker.com)
2. Cliquez sur **Repositories** → **Create Repository**
3. Nom du repository : `user-management-api`
4. Visibilité : **Public** (ou Private selon vos besoins)
5. Cliquez sur **Create**

### Étape 4 : Configurer les secrets GitHub

1. Allez dans votre repository GitHub
2. Cliquez sur **Settings** → **Secrets and variables** → **Actions**
3. Cliquez sur **New repository secret**

**Secret 1 : DOCKER_USERNAME**
- Name : `DOCKER_USERNAME`
- Secret : Votre nom d'utilisateur Docker Hub
- Cliquez sur **Add secret**

**Secret 2 : DOCKER_PASSWORD**
- Name : `DOCKER_PASSWORD`
- Secret : Le token d'accès que vous avez copié
- Cliquez sur **Add secret**

### Étape 5 : Mettre à jour le workflow

Éditez `.github/workflows/ci.yml` :

```yaml
env:
  DOCKER_IMAGE_NAME: VOTRE_USERNAME/user-management-api  # ← Changez ici
  DOCKER_REGISTRY: docker.io
```

Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur Docker Hub.

---

## 📦 Configuration GitHub Container Registry (GHCR)

### Alternative à Docker Hub (gratuit et illimité)

### Étape 1 : Créer un Personal Access Token

1. Allez dans **Settings** de votre profil GitHub (pas le repo)
2. **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. Cliquez sur **Generate new token** → **Generate new token (classic)**
4. Nom du token : `GHCR_CI_CD`
5. Sélectionnez les scopes suivants :
   - ✅ `write:packages`
   - ✅ `read:packages`
   - ✅ `delete:packages`
6. Cliquez sur **Generate token**
7. **⚠️ IMPORTANT** : Copiez le token immédiatement

### Étape 2 : Configurer le secret GitHub

1. Allez dans votre repository GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret**
   - Name : `GHCR_TOKEN`
   - Secret : Le token PAT que vous avez copié
   - Cliquez sur **Add secret**

### Étape 3 : Modifier le workflow

Éditez `.github/workflows/ci.yml` :

```yaml
env:
  DOCKER_IMAGE_NAME: ghcr.io/YOUR_USERNAME/user-management-api
  DOCKER_REGISTRY: ghcr.io

# Dans le job "push", remplacez la section login par :
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GHCR_TOKEN }}
```

---

## 🔧 Variables d'environnement

### Variables optionnelles

Vous pouvez également configurer des **variables** (non secrètes) :

1. **Settings** → **Secrets and variables** → **Actions** → **Variables**
2. Cliquez sur **New repository variable**

Exemples de variables utiles :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `PYTHON_VERSION` | Version Python à utiliser | `3.11` |
| `DOCKER_TAG` | Tag Docker par défaut | `latest` |
| `ENVIRONMENT` | Environnement de déploiement | `production` |

---

## ✅ Vérification

### 1. Vérifier les secrets

```bash
# Les secrets doivent être configurés (vous ne pouvez pas voir leur valeur)
# Dans Settings → Secrets and variables → Actions → Repository secrets
```

Vous devriez voir :
- ✅ `DOCKER_USERNAME`
- ✅ `DOCKER_PASSWORD`

### 2. Tester le pipeline

1. Faites un petit changement dans le code
2. Commit et push vers GitHub :

```bash
git add .
git commit -m "test: verify CI/CD pipeline"
git push origin main
```

3. Allez dans **Actions** → Le workflow devrait démarrer automatiquement
4. Vérifiez que tous les jobs passent (vert ✅)

### 3. Vérifier l'image Docker

**Pour Docker Hub :**
```bash
# L'image devrait être disponible sur Docker Hub
docker pull votre-username/user-management-api:latest
```

**Pour GHCR :**
```bash
# L'image devrait être disponible sur GHCR
docker pull ghcr.io/votre-username/user-management-api:latest
```

---

## 🔍 Dépannage

### Erreur : "Invalid username or password"

**Cause** : Token ou username incorrect

**Solution** :
1. Vérifiez que `DOCKER_USERNAME` est bien votre username (pas votre email)
2. Régénérez un nouveau token Docker Hub
3. Mettez à jour le secret `DOCKER_PASSWORD`

### Erreur : "denied: requested access to the resource is denied"

**Cause** : Le repository Docker Hub n'existe pas ou permissions insuffisantes

**Solution** :
1. Créez le repository sur Docker Hub
2. Vérifiez que le nom dans `DOCKER_IMAGE_NAME` correspond exactement
3. Vérifiez que le token a les permissions Write

### Erreur : "Error: buildx failed with: ERROR: failed to solve"

**Cause** : Problème lors du build Docker

**Solution** :
1. Testez le build localement : `docker build -t test .`
2. Vérifiez les logs détaillés dans GitHub Actions
3. Assurez-vous que tous les fichiers nécessaires sont présents

### Le workflow ne se déclenche pas

**Cause** : Configuration du déclencheur incorrecte

**Solution** :
1. Vérifiez que vous pushez sur la branche `main` ou `develop`
2. Vérifiez la section `on:` dans `.github/workflows/ci.yml`
3. Consultez l'onglet **Actions** pour voir les erreurs

### L'image n'est pas pushée sur Docker Hub

**Cause** : Le job "push" ne s'exécute que sur la branche `main`

**Solution** :
```yaml
# Dans ci.yml, cette condition détermine quand pusher
if: github.event_name == 'push' && github.ref == 'refs/heads/main'

# Pour tester sur develop aussi, changez en :
if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
```

---

## 📚 Ressources supplémentaires

- [Documentation Docker Hub](https://docs.docker.com/docker-hub/)
- [Documentation GitHub Actions](https://docs.github.com/en/actions)
- [Documentation GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
