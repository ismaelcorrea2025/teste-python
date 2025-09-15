from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import jwt

# ---------------- CONFIG ----------------
SECRET_KEY = "minha_chave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(title="E-commerce API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ---------------- MODELOS ----------------
class User(BaseModel):
    id: int
    username: str
    password: str

class Product(BaseModel):
    id: int
    name: str
    price: float

class ProductCreate(BaseModel):
    name: str
    price: float

class CartItem(BaseModel):
    id: int
    product: Product

# ---------------- DADOS DE EXEMPLO ----------------
users_db = [User(id=1, username="admin", password="1234")]
products_db = [
    Product(id=1, name="Notebook", price=3500),
    Product(id=2, name="Mouse", price=120)
]
cart_db: List[CartItem] = []

# ---------------- FUNÇÕES AUX ----------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = next((u for u in users_db if u.username == username), None)
        if not user:
            raise HTTPException(status_code=401, detail="Usuário inválido")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

# ---------------- AUTENTICAÇÃO ----------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = next((u for u in users_db if u.username == form_data.username and u.password == form_data.password), None)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
def logout():
    return {"message": "Logout realizado com sucesso"}

# ---------------- PRODUTOS ----------------
@app.get("/api/products", response_model=List[Product])
def get_products():
    return products_db

@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@app.get("/api/products/search", response_model=List[Product])
def search_products(q: str = Query(..., description="Nome do produto")):
    return [p for p in products_db if q.lower() in p.name.lower()]

@app.post("/api/products/add", response_model=Product)
def add_product(new_product: ProductCreate, user: User = Depends(get_current_user)):
    product = Product(id=len(products_db)+1, name=new_product.name, price=new_product.price)
    products_db.append(product)
    return product

@app.put("/api/products/update/{product_id}", response_model=Product)
def update_product(product_id: int, updated: ProductCreate, user: User = Depends(get_current_user)):
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    product.name = updated.name
    product.price = updated.price
    return product

@app.delete("/api/products/delete/{product_id}")
def delete_product(product_id: int, user: User = Depends(get_current_user)):
    global products_db
    products_db = [p for p in products_db if p.id != product_id]
    return {"message": "Produto removido"}

# ---------------- CARRINHO ----------------
@app.post("/api/cart/add/{product_id}", response_model=CartItem)
def add_to_cart(product_id: int, user: User = Depends(get_current_user)):
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    cart_item = CartItem(id=len(cart_db)+1, product=product)
    cart_db.append(cart_item)
    return cart_item

@app.delete("/api/cart/remove/{item_id}")
def remove_from_cart(item_id: int, user: User = Depends(get_current_user)):
    global cart_db
    cart_db = [c for c in cart_db if c.id != item_id]
    return {"message": "Item removido do carrinho"}

@app.get("/api/cart", response_model=List[CartItem])
def get_cart(user: User = Depends(get_current_user)):
    return cart_db

@app.post("/api/cart/checkout")
def checkout(user: User = Depends(get_current_user)):
    global cart_db
    cart_db = []
    return {"message": "Compra finalizada com sucesso!"}