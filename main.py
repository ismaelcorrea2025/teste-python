# ---------------- IMPORTS ----------------
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt

from database import engine, SessionLocal
from models_base import Base
from models.user import UserDB
from models.product import ProductDB
from models.cart_item import CartItemDB
from sqlalchemy.orm import Session

# ---------------- CONFIGURAÇÕES ----------------
SECRET_KEY = "minha_chave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ---------------- INICIALIZAÇÃO ----------------
app = FastAPI(title="E-commerce API")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajuste para seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria tabelas no banco
Base.metadata.create_all(bind=engine)

# ---------------- DEPENDÊNCIA DO BANCO ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- SCHEMAS Pydantic ----------------
class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # Pydantic v2

class Product(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    price: float

class CartItem(BaseModel):
    id: int
    product: Product

    class Config:
        from_attributes = True

# ---------------- FUNÇÕES AUXILIARES ----------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuário inválido")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

# ---------------- ROTA RAIZ ----------------
@app.get("/")
def root():
    return {"message": "API E-commerce funcionando!"}

# ---------------- AUTENTICAÇÃO ----------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(
        UserDB.username == form_data.username,
        UserDB.password == form_data.password  # ⚠️ Use hash em produção!
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=User)
def register(new_user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.username == new_user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    user = UserDB(username=new_user.username, password=new_user.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ---------------- PRODUTOS ----------------
@app.get("/api/products", response_model=List[Product])
def get_products(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()

@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@app.get("/api/products/search", response_model=List[Product])
def search_products(q: str = Query(..., description="Nome do produto"), db: Session = Depends(get_db)):
    return db.query(ProductDB).filter(ProductDB.name.ilike(f"%{q}%")).all()

@app.post("/api/products/add", response_model=Product)
def add_product(new_product: ProductCreate, db: Session = Depends(get_db), user: UserDB = Depends(get_current_user)):
    product = ProductDB(name=new_product.name, price=new_product.price)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.put("/api/products/update/{product_id}", response_model=Product)
def update_product(product_id: int, updated: ProductCreate, db: Session = Depends(get_db), user: UserDB = Depends(get_current_user)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    product.name = updated.name
    product.price = updated.price
    db.commit()
    db.refresh(product)
    return product

@app.delete("/api/products/delete/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user: UserDB = Depends(get_current_user)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(product)
    db.commit()
    return {"message": "Produto removido"}

# ---------------- CARRINHO ----------------
@app.post("/api/cart/add/{product_id}", response_model=CartItem)
def add_to_cart(product_id: int, db: Session = Depends(get_db), user: UserDB = Depends(get_current_user)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    cart_item = CartItemDB(user_id=user.id, product_id=product.id)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

@app.delete("/api/cart/remove/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db), user: UserDB = Depends(get_current_user)):
    item = db.query(CartItemDB).filter(CartItemDB.id == item_id, CartItemDB.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(item)
    db.commit()
    return {"message": "Item removido do carrinho"}

@app.get("/api/cart", response_model=List[CartItem])
def get_cart(db: Session = Depends(get_db), user: UserDB = Depends(get_current_user)):
    return db.query(CartItemDB).filter(CartItemDB.user_id == user.id).all()

@app.post("/api/cart/checkout")
def checkout(db: Session = Depends(get_db), user: UserDB = Depends(get_current_user)):
    db.query(CartItemDB).filter(CartItemDB.user_id == user.id).delete()
    db.commit()
    return {"message": "Compra finalizada com sucesso!"}