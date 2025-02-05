from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os

# Get database URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

# Create database engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Customer(Base):
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact = Column(String)
    address = Column(String)
    collections = relationship("Collection", back_populates="customer")

class Collection(Base):
    __tablename__ = 'collections'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    weight = Column(Float, nullable=False)
    customer = relationship("Customer", back_populates="collections")

# Create tables
def init_db():
    Base.metadata.create_all(engine)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
