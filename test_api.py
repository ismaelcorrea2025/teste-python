import httpx

BASE_URL = "http://127.0.0.1:8000"

def main():
    with httpx.Client(base_url=BASE_URL) as client:
        # ---------------- Registro ----------------
        print("1️⃣ Registrando usuário...")
        response = client.post("/register", json={"username": "ismael", "password": "123456"})
        print(response.status_code, response.json())

        # ---------------- Login ----------------
        print("2️⃣ Fazendo login...")
        response = client.post("/token", data={"username": "ismael", "password": "123456"})
        print(response.status_code, response.json())
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # ---------------- Criar produto ----------------
        print("3️⃣ Criando produto...")
        response = client.post("/products", json={"name": "Notebook", "price": 3500.50})
        print(response.status_code, response.json())
        product_id = response.json()["id"]

        # ---------------- Listar produtos ----------------
        print("4️⃣ Listando produtos...")
        response = client.get("/products")
        print(response.status_code, response.json())

        # ---------------- Atualizar produto ----------------
        print("5️⃣ Atualizando produto...")
        response = client.put(f"/products/{product_id}", json={"price": 3600.0})
        print(response.status_code, response.json())

        # ---------------- Adicionar ao carrinho ----------------
        print("6️⃣ Adicionando item ao carrinho...")
        response = client.post("/cart", json={"product_id": product_id, "quantity": 2}, headers=headers)
        print(response.status_code, response.json())
        cart_item_id = response.json()["id"]

        # ---------------- Listar carrinho ----------------
        print("7️⃣ Listando carrinho...")
        response = client.get("/cart", headers=headers)
        print(response.status_code, response.json())

        # ---------------- Atualizar item do carrinho ----------------
        print("8️⃣ Atualizando item do carrinho...")
        response = client.put(f"/cart/{cart_item_id}", json={"quantity": 5}, headers=headers)
        print(response.status_code, response.json())

        # ---------------- Deletar item do carrinho ----------------
        print("9️⃣ Deletando item do carrinho...")
        response = client.delete(f"/cart/{cart_item_id}", headers=headers)
        print(response.status_code)

        # ---------------- Atualizar usuário ----------------
        print("🔟 Atualizando usuário...")
        response = client.put("/users/me", json={"username": "ismael2", "password": "654321"}, headers=headers)
        print(response.status_code, response.json())

        # ---------------- Deletar usuário ----------------
        print("1️⃣1️⃣ Deletando usuário...")
        response = client.delete("/users/me", headers=headers)
        print(response.status_code)

if __name__ == "__main__":
    main()