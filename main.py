from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://itech_l1q2_user:AoqQkrtzrQW7WEDOJdh0C6hhlY5Xe3sv@dpg-cuvnsbggph6c73ev87g0-a/itech_l1q2"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Models
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String)
    buying_price = Column(Float)
    selling_price = Column(Float)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Float)

class Stock(Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, ForeignKey("products.name"))
    product_type = Column(String)
    quantity = Column(Integer)
    price_per_unit = Column(Float)

Base.metadata.create_all(bind=engine)

# Pydantic Models
class ProductBase(BaseModel):
    name: str
    type: str
    buying_price: float
    selling_price: float

class ServiceBase(BaseModel):
    name: str
    description: str
    price: float

class StockBase(BaseModel):
    product_name: str
    product_type: str
    quantity: int
    price_per_unit: float

# FastAPI App
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (replace with your frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes for Products
@app.post("/products/", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductBase, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[ProductBase])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.put("/products/{name}/{type}")
def update_product(name: str, type: str, product: ProductBase, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.name == name, Product.type == type).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{name}/{type}")
def delete_product(name: str, type: str, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.name == name, Product.type == type).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

# Routes for Services
@app.post("/services/", status_code=status.HTTP_201_CREATED)
def create_service(service: ServiceBase, db: Session = Depends(get_db)):
    db_service = Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@app.get("/services/", response_model=List[ServiceBase])
def get_services(db: Session = Depends(get_db)):
    return db.query(Service).all()

@app.put("/services/{name}")
def update_service(name: str, service: ServiceBase, db: Session = Depends(get_db)):
    db_service = db.query(Service).filter(Service.name == name).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    for key, value in service.dict().items():
        setattr(db_service, key, value)
    db.commit()
    db.refresh(db_service)
    return db_service

@app.delete("/services/{name}")
def delete_service(name: str, db: Session = Depends(get_db)):
    db_service = db.query(Service).filter(Service.name == name).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(db_service)
    db.commit()
    return {"message": "Service deleted successfully"}

# Routes for Stock
@app.post("/stock/", status_code=status.HTTP_201_CREATED)
def create_stock(stock: StockBase, db: Session = Depends(get_db)):
    db_stock = Stock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@app.get("/stock/", response_model=List[StockBase])
def get_stock(db: Session = Depends(get_db)):
    return db.query(Stock).all()

@app.put("/stock/{product_name}/{product_type}")
def update_stock(product_name: str, product_type: str, stock: StockBase, db: Session = Depends(get_db)):
    db_stock = db.query(Stock).filter(Stock.product_name == product_name, Stock.product_type == product_type).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock item not found")
    for key, value in stock.dict().items():
        setattr(db_stock, key, value)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@app.delete("/stock/{product_name}/{product_type}")
def delete_stock(product_name: str, product_type: str, db: Session = Depends(get_db)):
    db_stock = db.query(Stock).filter(Stock.product_name == product_name, Stock.product_type == product_type).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock item not found")
    db.delete(db_stock)
    db.commit()
    return {"message": "Stock item deleted successfully"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
