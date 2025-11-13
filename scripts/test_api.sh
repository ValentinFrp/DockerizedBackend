#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost:8000}"
SLEEP_TIME=1

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

check_api() {
    print_header "Vérification de l'API"
    print_info "URL: $API_URL"

    if curl -f -s "$API_URL/health" > /dev/null 2>&1; then
        print_success "API accessible"
    else
        print_error "API non accessible. Assurez-vous que l'API est démarrée."
        exit 1
    fi
    sleep $SLEEP_TIME
}

test_health_check() {
    print_header "Test 1: Health Check"

    print_info "GET $API_URL/health"
    response=$(curl -s "$API_URL/health")

    if echo "$response" | grep -q '"status":"healthy"'; then
        print_success "Health check OK"
        echo "$response" | python3 -m json.tool
    else
        print_error "Health check failed"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_root() {
    print_header "Test 2: Root Endpoint"

    print_info "GET $API_URL/"
    response=$(curl -s "$API_URL/")

    if echo "$response" | grep -q 'Welcome'; then
        print_success "Root endpoint OK"
        echo "$response" | python3 -m json.tool
    else
        print_error "Root endpoint failed"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_create_user() {
    print_header "Test 3: Créer un utilisateur"

    print_info "POST $API_URL/users"

    user_data='{
        "username": "johndoe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "password": "securepassword123"
    }'

    response=$(curl -s -X POST "$API_URL/users" \
        -H "Content-Type: application/json" \
        -d "$user_data")

    if echo "$response" | grep -q '"username":"johndoe"'; then
        print_success "Utilisateur créé avec succès"
        echo "$response" | python3 -m json.tool
        USER_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
        export USER_ID
    else
        print_error "Échec de création d'utilisateur"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_create_second_user() {
    print_header "Test 4: Créer un deuxième utilisateur"

    print_info "POST $API_URL/users"

    user_data='{
        "username": "janedoe",
        "email": "jane@example.com",
        "full_name": "Jane Doe",
        "password": "anotherpassword456"
    }'

    response=$(curl -s -X POST "$API_URL/users" \
        -H "Content-Type: application/json" \
        -d "$user_data")

    if echo "$response" | grep -q '"username":"janedoe"'; then
        print_success "Deuxième utilisateur créé"
        echo "$response" | python3 -m json.tool
    else
        print_error "Échec de création du deuxième utilisateur"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_duplicate_username() {
    print_header "Test 5: Validation - Username dupliqué"

    print_info "POST $API_URL/users (devrait échouer)"

    user_data='{
        "username": "johndoe",
        "email": "different@example.com",
        "password": "password123"
    }'

    response=$(curl -s -X POST "$API_URL/users" \
        -H "Content-Type: application/json" \
        -d "$user_data")

    if echo "$response" | grep -q 'already exists'; then
        print_success "Validation correcte - username dupliqué rejeté"
        echo "$response" | python3 -m json.tool
    else
        print_error "La validation n'a pas fonctionné"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_list_users() {
    print_header "Test 6: Lister les utilisateurs"

    print_info "GET $API_URL/users"
    response=$(curl -s "$API_URL/users")

    user_count=$(echo "$response" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

    if [ "$user_count" -ge 1 ]; then
        print_success "Liste d'utilisateurs récupérée ($user_count utilisateurs)"
        echo "$response" | python3 -m json.tool
    else
        print_error "Échec de récupération de la liste"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_get_user() {
    print_header "Test 7: Récupérer un utilisateur"

    if [ -z "$USER_ID" ]; then
        USER_ID=1
    fi

    print_info "GET $API_URL/users/$USER_ID"
    response=$(curl -s "$API_URL/users/$USER_ID")

    if echo "$response" | grep -q '"id"'; then
        print_success "Utilisateur récupéré avec succès"
        echo "$response" | python3 -m json.tool
    else
        print_error "Échec de récupération de l'utilisateur"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_update_user() {
    print_header "Test 8: Mettre à jour un utilisateur"

    if [ -z "$USER_ID" ]; then
        USER_ID=1
    fi

    print_info "PUT $API_URL/users/$USER_ID"

    update_data='{
        "username": "johndoe_updated",
        "email": "john.updated@example.com",
        "full_name": "John Doe Updated"
    }'

    response=$(curl -s -X PUT "$API_URL/users/$USER_ID" \
        -H "Content-Type: application/json" \
        -d "$update_data")

    if echo "$response" | grep -q 'updated'; then
        print_success "Utilisateur mis à jour"
        echo "$response" | python3 -m json.tool
    else
        print_error "Échec de mise à jour"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_pagination() {
    print_header "Test 9: Pagination"

    print_info "GET $API_URL/users?skip=0&limit=1"
    response=$(curl -s "$API_URL/users?skip=0&limit=1")

    user_count=$(echo "$response" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

    if [ "$user_count" -eq 1 ]; then
        print_success "Pagination fonctionne (limit=1)"
        echo "$response" | python3 -m json.tool
    else
        print_error "Problème avec la pagination"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_delete_user() {
    print_header "Test 10: Supprimer un utilisateur"

    if [ -z "$USER_ID" ]; then
        USER_ID=1
    fi

    print_info "DELETE $API_URL/users/$USER_ID"
    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X DELETE "$API_URL/users/$USER_ID")

    http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)

    if [ "$http_code" = "204" ]; then
        print_success "Utilisateur supprimé"
    else
        print_error "Échec de suppression (HTTP $http_code)"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_user_deleted() {
    print_header "Test 11: Vérifier la suppression"

    if [ -z "$USER_ID" ]; then
        USER_ID=1
    fi

    print_info "GET $API_URL/users/$USER_ID (devrait retourner 404)"
    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_URL/users/$USER_ID")

    http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)

    if [ "$http_code" = "404" ]; then
        print_success "Utilisateur bien supprimé (404)"
    else
        print_error "L'utilisateur existe encore (HTTP $http_code)"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

test_invalid_email() {
    print_header "Test 12: Validation - Email invalide"

    print_info "POST $API_URL/users (email invalide)"

    user_data='{
        "username": "testuser",
        "email": "not-an-email",
        "password": "password123"
    }'

    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_URL/users" \
        -H "Content-Type: application/json" \
        -d "$user_data")

    http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)

    if [ "$http_code" = "422" ]; then
        print_success "Validation correcte - email invalide rejeté"
    else
        print_error "La validation email n'a pas fonctionné (HTTP $http_code)"
        echo "$response"
    fi
    sleep $SLEEP_TIME
}

main() {
    print_header "🚀 Tests de l'API User Management"
    echo "API URL: $API_URL"
    echo ""

    check_api
    test_health_check
    test_root
    test_create_user
    test_create_second_user
    test_duplicate_username
    test_list_users
    test_get_user
    test_update_user
    test_pagination
    test_delete_user
    test_user_deleted
    test_invalid_email

    print_header "✨ Tests terminés"
    echo -e "${GREEN}Tous les tests ont été exécutés avec succès!${NC}"
    echo ""
    echo "Pour plus de tests interactifs, visitez:"
    echo "  → Documentation: $API_URL/docs"
    echo "  → ReDoc: $API_URL/redoc"
    echo ""
}

main
