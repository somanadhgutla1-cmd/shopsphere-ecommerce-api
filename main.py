from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import auth
from database import engine, get_db

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="🛒 ShopSphere E-Commerce API",
    description="Full-stack REST API with SQLite DB, JWT Auth, and Product Catalog.",
    version="1.0.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- API ENDPOINTS ----------------

@app.get("/")
def root():
    return {"message": "Welcome to ShopSphere Full-Stack E-Commerce API! Visit /docs for Swagger interactive documentation."}

# --- AUTH ENDPOINTS ---
@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- PRODUCT ENDPOINTS ---
@app.get("/products", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    
    # Auto-seed initial products if DB is empty
    if not products:
        sample_products = [
            models.Product(title="Wireless Noise-Canceling Headphones", description="High fidelity audio with 30hr battery life.", price=199.99, category="Electronics", image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"),
            models.Product(title="Smart Fitness Watch", description="Track workouts, heart rate, and sleep quality.", price=129.50, category="Electronics", image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"),
            models.Product(title="Classic Leather Backpack", description="Durable handcrafted leather laptop bag.", price=89.99, category="Fashion", image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500"),
            models.Product(title="Ergonomic Desk Chair", description="Breathable mesh back with lumber support.", price=249.00, category="Furniture", image_url="https://images.unsplash.com/photo-1580481072645-022f9a6d1270?w=500")
        ]
        db.add_all(sample_products)
        db.commit()
        products = db.query(models.Product).all()
        
    return products

@app.post("/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_product = models.Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product
