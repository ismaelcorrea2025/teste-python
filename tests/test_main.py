import pytest
from fastapi.testclient import TestClient
from main import app, SessionLocal, UserDB
from sqlalchemy.orm import Session

client = TestClient(app)

# Variáveis globais de teste
TOKEN = None
HEADERS = None
PRODUCT_ID = None
CART_ITEM_ID = None

# ---------------- Função auxiliar ----------------
def delete_user_if_exists(username: str):
    with SessionLocal() as db:
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if user:
            db.delete(user)
            db.commit()

# ---------------- Testes ----------------
def test_register_and_login():
    global TOKEN, HEADERS

    username = "ismael_test"
    password = "123456"

    # Limpar usuário caso exista
    delete_user_if_exists(username)

    # Registro
    response = client.post("/register", json={"username": username, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username

    # Login
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    TOKEN = data["access_token"]
    HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def test_product_crud():
    global PRODUCT_ID

    # Criar produto
    response = client.post("/products", json={"name": "Notebook", "price": 3500.50})
    assert response.status_code == 200
    data = response.json()
    PRODUCT_ID = data["id"]
    assert data["name"] == "Notebook"

    # Listar produtos
    response = client.get("/products")
    assert response.status_code == 200
    assert any(p["id"] == PRODUCT_ID for p in response.json())

    # Atualizar produto
    response = client.put(f"/products/{PRODUCT_ID}", json={"price": 3600.0})
    assert response.status_code == 200
    assert response.json()["price"] == 3600.0

    # Deletar produto
    response = client.delete(f"/products/{PRODUCT_ID}")
    assert response.status_code == 204


def test_cart_crud():
    global PRODUCT_ID, CART_ITEM_ID

    # Criar produto para o carrinho
    response = client.post("/products", json={"name": "Mouse", "price": 150.0})
    assert response.status_code == 200
    PRODUCT_ID = response.json()["id"]

    # Adicionar ao carrinho
    response = client.post("/cart", json={"product_id": PRODUCT_ID, "quantity": 2}, headers=HEADERS)
    assert response.status_code == 200
    CART_ITEM_ID = response.json()["id"]

    # Listar carrinho
    response = client.get("/cart", headers=HEADERS)
    assert response.status_code == 200
    assert any(item["id"] == CART_ITEM_ID for item in response.json())

    # Atualizar item do carrinho
    response = client.put(f"/cart/{CART_ITEM_ID}", json={"quantity": 5}, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["quantity"] == 5

    # Deletar item do carrinho
    response = client.delete(f"/cart/{CART_ITEM_ID}", headers=HEADERS)
    assert response.status_code == 204

    # Deletar produto usado
    client.delete(f"/products/{PRODUCT_ID}")


def test_user_update_and_delete():
    username = "ismael_test"
    new_username = "ismael_test2"
    password = "123456"
    new_password = "654321"

    # Atualizar usuário
    response = client.put("/users/me", json={"username": new_username, "password": new_password}, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["username"] == new_username

    # Login com novo username e senha
    response = client.post("/token", data={"username": new_username, "password": new_password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Deletar usuário
    response = client.delete("/users/me", headers=headers)
    assert response.status_code == 204