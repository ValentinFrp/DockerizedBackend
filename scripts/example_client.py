#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Optional

import requests

API_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}


class UserManagementClient:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _handle_response(self, response: requests.Response) -> Dict:
        try:
            response.raise_for_status()
            if response.status_code == 204:
                return {"message": "Success - No content"}
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"❌ Erreur HTTP: {e}")
            if response.text:
                print(f"Détails: {response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            sys.exit(1)

    def health_check(self) -> Dict:
        print("🔍 Vérification du health check...")
        response = self.session.get(f"{self.base_url}/health")
        return self._handle_response(response)

    def create_user(
        self, username: str, email: str, password: str, full_name: Optional[str] = None
    ) -> Dict:
        print(f"➕ Création de l'utilisateur '{username}'...")
        data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name,
        }
        response = self.session.post(f"{self.base_url}/users", json=data)
        return self._handle_response(response)

    def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        print(f"📋 Récupération des utilisateurs (skip={skip}, limit={limit})...")
        response = self.session.get(
            f"{self.base_url}/users", params={"skip": skip, "limit": limit}
        )
        return self._handle_response(response)

    def get_user(self, user_id: int) -> Dict:
        print(f"🔍 Récupération de l'utilisateur {user_id}...")
        response = self.session.get(f"{self.base_url}/users/{user_id}")
        return self._handle_response(response)

    def update_user(
        self, user_id: int, username: str, email: str, full_name: Optional[str] = None
    ) -> Dict:
        print(f"✏️  Mise à jour de l'utilisateur {user_id}...")
        data = {"username": username, "email": email, "full_name": full_name}
        response = self.session.put(f"{self.base_url}/users/{user_id}", json=data)
        return self._handle_response(response)

    def delete_user(self, user_id: int) -> Dict:
        print(f"🗑️  Suppression de l'utilisateur {user_id}...")
        response = self.session.delete(f"{self.base_url}/users/{user_id}")
        return self._handle_response(response)


def print_json(data: Dict | List, title: str = ""):
    if title:
        print(f"\n{'=' * 60}")
        print(f"📄 {title}")
        print(f"{'=' * 60}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()


def demo_workflow():
    print("\n" + "=" * 60)
    print("🚀 Démonstration de l'API User Management")
    print("=" * 60 + "\n")

    client = UserManagementClient()

    try:
        print("\n📍 Étape 1: Health Check")
        print("-" * 60)
        health = client.health_check()
        print_json(health, "Statut de l'API")

        print("\n📍 Étape 2: Création d'utilisateurs")
        print("-" * 60)

        user1 = client.create_user(
            username="alice_smith",
            email="alice@example.com",
            password="SecurePass123!",
            full_name="Alice Smith",
        )
        print_json(user1, "Utilisateur 1 créé")

        user2 = client.create_user(
            username="bob_jones",
            email="bob@example.com",
            password="AnotherPass456!",
            full_name="Bob Jones",
        )
        print_json(user2, "Utilisateur 2 créé")

        user3 = client.create_user(
            username="charlie_brown",
            email="charlie@example.com",
            password="MyPassword789!",
        )
        print_json(user3, "Utilisateur 3 créé (sans full_name)")

        print("\n📍 Étape 3: Liste des utilisateurs")
        print("-" * 60)
        users = client.list_users()
        print_json(users, f"Liste complète ({len(users)} utilisateurs)")

        print("\n📍 Étape 4: Récupération d'un utilisateur")
        print("-" * 60)
        user_id = user1["id"]
        user = client.get_user(user_id)
        print_json(user, f"Utilisateur {user_id}")

        print("\n📍 Étape 5: Mise à jour d'un utilisateur")
        print("-" * 60)
        updated_user = client.update_user(
            user_id=user_id,
            username="alice_smith_updated",
            email="alice.updated@example.com",
            full_name="Alice Smith (Updated)",
        )
        print_json(updated_user, "Utilisateur mis à jour")

        print("\n📍 Étape 6: Test de pagination")
        print("-" * 60)
        page1 = client.list_users(skip=0, limit=2)
        print_json(page1, "Page 1 (2 premiers utilisateurs)")

        page2 = client.list_users(skip=2, limit=2)
        print_json(page2, "Page 2 (utilisateurs suivants)")

        print("\n📍 Étape 7: Suppression d'un utilisateur")
        print("-" * 60)
        delete_result = client.delete_user(user2["id"])
        print_json(delete_result, "Résultat de la suppression")

        print("\n📍 Étape 8: Vérification après suppression")
        print("-" * 60)
        final_users = client.list_users()
        print_json(final_users, f"Liste finale ({len(final_users)} utilisateurs)")

        print("\n" + "=" * 60)
        print("✅ Démonstration terminée avec succès!")
        print("=" * 60)
        print(f"\n📊 Résumé:")
        print(f"  • Utilisateurs créés: 3")
        print(f"  • Utilisateurs supprimés: 1")
        print(f"  • Utilisateurs restants: {len(final_users)}")
        print(f"\n💡 Pour plus d'informations, visitez: {API_URL}/docs")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Démonstration interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {e}")
        sys.exit(1)


def demo_validation_errors():
    print("\n" + "=" * 60)
    print("🧪 Tests de validation")
    print("=" * 60 + "\n")

    client = UserManagementClient()

    print("\n🧪 Test 1: Email invalide")
    print("-" * 60)
    try:
        client.create_user(
            username="testuser1", email="not-an-email", password="password123"
        )
    except SystemExit:
        print("✅ Email invalide correctement rejeté\n")

    print("\n🧪 Test 2: Username trop court")
    print("-" * 60)
    try:
        client.create_user(
            username="ab", email="test@example.com", password="password123"
        )
    except SystemExit:
        print("✅ Username trop court correctement rejeté\n")

    print("\n🧪 Test 3: Mot de passe trop court")
    print("-" * 60)
    try:
        client.create_user(
            username="testuser3", email="test@example.com", password="short"
        )
    except SystemExit:
        print("✅ Mot de passe trop court correctement rejeté\n")


def interactive_mode():
    print("\n" + "=" * 60)
    print("🎮 Mode interactif")
    print("=" * 60 + "\n")

    client = UserManagementClient()

    while True:
        print("\nChoisissez une action:")
        print("  1. Créer un utilisateur")
        print("  2. Lister les utilisateurs")
        print("  3. Récupérer un utilisateur")
        print("  4. Mettre à jour un utilisateur")
        print("  5. Supprimer un utilisateur")
        print("  6. Health check")
        print("  0. Quitter")

        choice = input("\nVotre choix: ").strip()

        try:
            if choice == "0":
                print("\n👋 Au revoir!")
                break

            elif choice == "1":
                username = input("Username: ")
                email = input("Email: ")
                password = input("Password: ")
                full_name = input("Full name (optionnel): ") or None
                result = client.create_user(username, email, password, full_name)
                print_json(result)

            elif choice == "2":
                result = client.list_users()
                print_json(result)

            elif choice == "3":
                user_id = int(input("User ID: "))
                result = client.get_user(user_id)
                print_json(result)

            elif choice == "4":
                user_id = int(input("User ID: "))
                username = input("New username: ")
                email = input("New email: ")
                full_name = input("New full name (optionnel): ") or None
                result = client.update_user(user_id, username, email, full_name)
                print_json(result)

            elif choice == "5":
                user_id = int(input("User ID: "))
                result = client.delete_user(user_id)
                print_json(result)

            elif choice == "6":
                result = client.health_check()
                print_json(result)

            else:
                print("❌ Choix invalide")

        except ValueError as e:
            print(f"❌ Erreur de saisie: {e}")
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break


def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1]

        if mode == "demo":
            demo_workflow()
        elif mode == "validation":
            demo_validation_errors()
        elif mode == "interactive":
            interactive_mode()
        else:
            print(f"❌ Mode inconnu: {mode}")
            print_usage()
    else:
        demo_workflow()


def print_usage():
    print("\nUsage:")
    print("  python example_client.py [mode]")
    print("\nModes disponibles:")
    print("  demo        - Démonstration complète du workflow CRUD (défaut)")
    print("  validation  - Tests de validation des données")
    print("  interactive - Mode interactif")
    print("\nExemples:")
    print("  python example_client.py")
    print("  python example_client.py demo")
    print("  python example_client.py validation")
    print("  python example_client.py interactive")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir!")
        sys.exit(0)
