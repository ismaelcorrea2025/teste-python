from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from database import SessionLocal, engine, Base
from models.user import UserDB
from models.product import ProductDB
from models.cart_item import CartItemDB
from schemas.user import UserCreate, UserUpdate, User
from schemas.product import ProductCreate, ProductUpdate, Product
from schemas.cart_item import CartItemCreate, CartItemUpdate, CartItem

# Criar tabelas
Base.metadata.create_all(bind=engine)

# App FastAPI
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------------- Dependência do banco ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- Funções auxiliares ----------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ---------------- Usuários ----------------
@app.post("/register", response_model=User)
def register(new_user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.username == new_user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = UserDB(username=new_user.username, password=new_user.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}

@app.put("/users/me", response_model=User)
def update_user(user_update: UserUpdate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    if user_update.username:
        existing = db.query(UserDB).filter(UserDB.username == user_update.username).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = user_update.username
    if user_update.password:
        current_user.password = user_update.password
    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/users/me", status_code=204)
def delete_user(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return

# ---------------- Produtos ----------------
@app.post("/products", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductDB(name=product.name, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products", response_model=list[Product])
def list_products(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_update.name:
        product.name = product_update.name
    if product_update.price:
        product.price = product_update.price
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return

# ---------------- Carrinho ----------------
@app.post("/cart", response_model=CartItem)
def add_to_cart(item: CartItemCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_item = CartItemDB(user_id=current_user.id, product_id=item.product_id, quantity=item.quantity)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/cart", response_model=list[CartItem])
def list_cart(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return db.query(CartItemDB).filter(CartItemDB.user_id == current_user.id).all()

@app.put("/cart/{cart_item_id}", response_model=CartItem)
def update_cart_item(cart_item_id: int, item_update: CartItemUpdate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    cart_item = db.query(CartItemDB).filter(CartItemDB.id == cart_item_id, CartItemDB.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    cart_item.quantity = item_update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@app.delete("/cart/{cart_item_id}", status_code=204)
def delete_cart_item(cart_item_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    cart_item = db.query(CartItemDB).filter(CartItemDB.id == cart_item_id, CartItemDB.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return