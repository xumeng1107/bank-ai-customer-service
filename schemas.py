from pydantic import BaseModel
from typing import List, Optional


class User(BaseModel):
    id: int
    username: str
    name: str
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: User
    message: str
    suggestions: List[str]


class MessageRequest(BaseModel):
    username: str
    message: str


class Product(BaseModel):
    id: int
    name: str
    description: str
    risk_level: str
    min_amount: float
    annual_rate: float  # 年化收益率
    
    class Config:
        from_attributes = True


class ProductResponse(Product):
    pass


class Branch(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    hours: str
    
    class Config:
        from_attributes = True


class BranchResponse(Branch):
    pass


class MessageResponse(BaseModel):
    message: str
    suggestions: List[str]
    products: Optional[List[Product]] = None
    has_more_products: Optional[bool] = False
    branches: Optional[List[Branch]] = None
    need_followup: Optional[bool] = False
