from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String)


class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    balance = Column(Float)
    account_type = Column(String)


class Branch(Base):
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String)
    hours = Column(String)


class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    month = Column(String)
    income = Column(Float, default=0.0)
    expense = Column(Float, default=0.0)
    description = Column(String)


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    risk_level = Column(String)
    min_amount = Column(Float)
    annual_rate = Column(Float)  # 年化收益率
