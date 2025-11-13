.PHONY: help install test lint format clean docker-build docker-run docker-stop docker-clean all

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
ISORT := isort
DOCKER_IMAGE := user-management-api
DOCKER_TAG := latest

# Couleurs pour l'affichage
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Commandes d'aide
help:
	@echo "$(GREEN)User Management API - Commandes disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# Installation et configuration
install:
	@echo "$(GREEN)Installation des dépendances...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Installation terminée$(NC)"

install-dev: install
	@echo "$(GREEN)Installation des outils de développement...$(NC)"
	$(PIP) install black flake8 isort pytest-cov
	@echo "$(GREEN)✓ Installation dev terminée$(NC)"

# Tests et qualité de code
test:
	@echo "$(GREEN)Exécution des tests...$(NC)"
	$(PYTEST) tests/ -v

test-cov:
	@echo "$(GREEN)Exécution des tests avec couverture...$(NC)"
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Rapport de couverture généré dans htmlcov/$(NC)"

test-watch:
	@echo "$(GREEN)Tests en mode watch...$(NC)"
	$(PYTEST) tests/ -v --looponfail

lint:
	@echo "$(GREEN)Vérification du code avec Flake8...$(NC)"
	$(FLAKE8) src/ tests/ --max-line-length=88 --extend-ignore=E203,W503

format-check:
	@echo "$(GREEN)Vérification du formatage...$(NC)"
	$(BLACK) --check src/ tests/
	$(ISORT) --check-only src/ tests/

format:
	@echo "$(GREEN)Formatage du code...$(NC)"
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/
	@echo "$(GREEN)✓ Code formaté$(NC)"

check: lint format-check test
	@echo "$(GREEN)✓ Toutes les vérifications sont passées!$(NC)"

run:
	@echo "$(GREEN)Démarrage de l'API...$(NC)"
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	@echo "$(GREEN)Démarrage de l'API en mode production...$(NC)"
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker

docker-build:
	@echo "$(GREEN)Construction de l'image Docker...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✓ Image construite: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

docker-build-no-cache:
	@echo "$(GREEN)Construction de l'image Docker (sans cache)...$(NC)"
	docker build --no-cache -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✓ Image construite$(NC)"

docker-run:
	@echo "$(GREEN)Démarrage du conteneur...$(NC)"
	docker run -d -p 8000:8000 --name $(DOCKER_IMAGE) $(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(GREEN)✓ Conteneur démarré sur http://localhost:8000$(NC)"

docker-stop:
	@echo "$(YELLOW)Arrêt du conteneur...$(NC)"
	docker stop $(DOCKER_IMAGE) || true
	docker rm $(DOCKER_IMAGE) || true
	@echo "$(GREEN)✓ Conteneur arrêté$(NC)"

docker-logs:
	docker logs -f $(DOCKER_IMAGE)

docker-exec:
	docker exec -it $(DOCKER_IMAGE) /bin/sh

docker-clean: docker-stop
	@echo "$(YELLOW)Nettoyage Docker...$(NC)"
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) || true
	docker system prune -f
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

docker-compose-up:
	@echo "$(GREEN)Démarrage avec docker-compose...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services démarrés$(NC)"

docker-compose-down:
	@echo "$(YELLOW)Arrêt des services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services arrêtés$(NC)"

docker-compose-logs:
	docker-compose logs -f

# Nettoyage
clean:
	@echo "$(YELLOW)Nettoyage des fichiers temporaires...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f coverage.xml
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

clean-all: clean docker-clean
	@echo "$(GREEN)✓ Nettoyage complet terminé$(NC)"

# CI/CD Local
ci-local:
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)Simulation du pipeline CI/CD$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Vérification du formatage...$(NC)"
	@$(MAKE) format-check
	@echo ""
	@echo "$(YELLOW)2. Linting...$(NC)"
	@$(MAKE) lint
	@echo ""
	@echo "$(YELLOW)3. Tests avec couverture...$(NC)"
	@$(MAKE) test-cov
	@echo ""
	@echo "$(YELLOW)4. Construction Docker...$(NC)"
	@$(MAKE) docker-build
	@echo ""
	@echo "$(GREEN)✓ Pipeline CI réussi!$(NC)"

# Utilitaires
docs:
	@echo "$(GREEN)Ouverture de la documentation...$(NC)"
	@echo "Documentation disponible sur: http://localhost:8000/docs"

health:
	@echo "$(GREEN)Vérification du health check...$(NC)"
	@curl -f http://localhost:8000/health | python3 -m json.tool

version:
	@echo "$(GREEN)Versions:$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"

# Commande par défaut
all: clean install check docker-build

.DEFAULT_GOAL := help
