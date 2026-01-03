from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import User, Account, Branch, Bill, Product
from schemas import UserResponse, MessageRequest, MessageResponse, ProductResponse, BranchResponse
from qwen import generate_response, analyze_intent

# 用户上下文管理
user_context = {}
"""
user_context结构：
{
    "username": {
        "city": "杭州",  # 记录用户所在城市
        "financial_query": {
            "keywords": [],  # 记录之前的关键字
            "rate": None,  # 记录之前的年化收益率要求
            "rate_condition": None,  # 记录之前的年化收益率条件
            "amount": None,  # 记录之前的起购金额要求
            "amount_condition": None,  # 记录之前的起购金额条件
            "risk": None  # 记录之前的风险等级要求
        }
    }
}
"""

app = FastAPI(
    title="银行智能客服API",
    description="银行智能客服系统，基于通义千问大模型",
    version="1.0.0"
)


# 添加CORS中间件
# 在生产环境中，应该使用具体的前端域名而不是通配符
# 为了灵活部署，我们允许使用环境变量FRONTEND_URL指定允许的来源
# 如果没有设置，则允许所有来源（仅用于开发或测试）
import os

frontend_url = os.environ.get("FRONTEND_URL", "*")
allow_origins = [frontend_url] if frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # 允许所有来源或指定的前端URL
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# 挂载静态文件服务到 /static 路径
# 这允许访问静态资源，同时保持API路由的优先级
app.mount("/static", StaticFiles(directory="static-frontend"), name="static")

# 根路径返回前端页面
@app.get("/")
def serve_frontend():
    return FileResponse("static-frontend/index.html")


# 初始化模拟数据
@app.on_event("startup")
async def init_db():
    # 首先创建数据库表
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    # 检查是否已有数据
    try:
        if db.query(User).count() > 0:
            return
    except Exception:
        # 如果表不存在，会抛出异常，此时我们需要重新创建数据
        pass
    
    # 创建用户
    user = User(username="test", name="测试用户")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 创建账户
    account = Account(user_id=user.id, balance=50000.00, account_type="储蓄卡")
    db.add(account)
    
    # 创建网点
    branches = [
        # 北京网点
        Branch(name="总行营业部", address="北京市朝阳区建国路1号", phone="010-88888888", hours="周一至周五 9:00-17:00, 周六 9:00-12:00"),
        Branch(name="中关村支行", address="北京市海淀区中关村大街1号", phone="010-88889999", hours="周一至周五 9:00-17:00, 周日 9:00-12:00"),
        Branch(name="金融街支行", address="北京市西城区金融大街1号", phone="010-88887777", hours="周一至周五 9:00-17:00"),
        
        # 杭州网点
        Branch(name="杭州分行营业部", address="杭州市西湖区延安路1号", phone="0571-88888888", hours="周一至周五 9:00-17:00, 周六 9:00-12:00"),
        Branch(name="杭州江干支行", address="杭州市江干区钱江新城1号", phone="0571-88889999", hours="周一至周五 9:00-17:00, 周日 9:00-12:00"),
        Branch(name="杭州余杭支行", address="杭州市余杭区文一西路1号", phone="0571-88887777", hours="周一至周五 9:00-17:00")
    ]
    db.add_all(branches)
    
    # 创建账单
    bills = [
        # 2024年的账单数据
        Bill(user_id=user.id, month="2024-01", income=10000.00, expense=1200.00, description="1月收支"),
        Bill(user_id=user.id, month="2024-02", income=10000.00, expense=1500.00, description="2月收支"),
        Bill(user_id=user.id, month="2024-03", income=10000.00, expense=1800.00, description="3月收支"),
        
        # 2025年一整年的账单数据
        Bill(user_id=user.id, month="2025-01", income=12000.00, expense=1800.00, description="1月收支"),
        Bill(user_id=user.id, month="2025-02", income=12000.00, expense=1900.00, description="2月收支"),
        Bill(user_id=user.id, month="2025-03", income=12000.00, expense=2000.00, description="3月收支"),
        Bill(user_id=user.id, month="2025-04", income=12000.00, expense=2100.00, description="4月收支"),
        Bill(user_id=user.id, month="2025-05", income=12000.00, expense=2000.00, description="5月收支"),
        Bill(user_id=user.id, month="2025-06", income=12000.00, expense=2200.00, description="6月收支"),
        Bill(user_id=user.id, month="2025-07", income=12000.00, expense=2300.00, description="7月收支"),
        Bill(user_id=user.id, month="2025-08", income=12000.00, expense=2400.00, description="8月收支"),
        Bill(user_id=user.id, month="2025-09", income=12000.00, expense=2200.00, description="9月收支"),
        Bill(user_id=user.id, month="2025-10", income=12000.00, expense=2000.00, description="10月收支"),
        Bill(user_id=user.id, month="2025-11", income=12000.00, expense=2200.00, description="11月收支"),
        Bill(user_id=user.id, month="2025-12", income=12000.00, expense=2500.00, description="12月收支")
    ]
    db.add_all(bills)
    
    # 创建更丰富的理财产品数据
    products = [
        # 低风险产品
        Product(name="天天利宝", description="低风险，灵活存取，适合短期闲置资金", risk_level="低", min_amount=1.00, annual_rate=2.5),
        Product(name="稳健收益A", description="低风险，定期30天，收益稳定", risk_level="低", min_amount=100.00, annual_rate=3.2),
        Product(name="安心保本", description="低风险，保本保息，适合保守型投资者", risk_level="低", min_amount=1000.00, annual_rate=3.0),
        Product(name="稳健增长", description="低风险，长期持有，收益稳健增长", risk_level="低", min_amount=500.00, annual_rate=3.5),
        
        # 中风险产品
        Product(name="平衡配置", description="中等风险，股债平衡，适合平衡型投资者", risk_level="中", min_amount=500.00, annual_rate=5.5),
        Product(name="成长精选", description="中等风险，投资成长型企业，收益潜力较大", risk_level="中", min_amount=800.00, annual_rate=6.2),
        Product(name="稳健增强", description="中等风险，在稳健基础上增强收益", risk_level="中", min_amount=1000.00, annual_rate=5.0),
        Product(name="行业精选", description="中等风险，聚焦优质行业，把握行业机遇", risk_level="中", min_amount=300.00, annual_rate=5.8),
        
        # 高风险产品
        Product(name="进取先锋", description="高风险，投资股票市场，收益潜力大", risk_level="高", min_amount=100.00, annual_rate=8.5),
        Product(name="成长动力", description="高风险，投资成长股，追求高回报", risk_level="高", min_amount=500.00, annual_rate=9.2),
        Product(name="科技前沿", description="高风险，投资科技行业，把握科技趋势", risk_level="高", min_amount=300.00, annual_rate=10.0),
        Product(name="创业机会", description="高风险，投资创业企业，高风险高回报", risk_level="高", min_amount=200.00, annual_rate=12.0)
    ]
    db.add_all(products)
    
    db.commit()


# 用户登录
@app.post("/login/{username}", response_model=UserResponse)
def login(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "user": user,
        "message": "欢迎使用银行智能客服！我可以为您提供以下服务：",
        "suggestions": ["查询账户", "查询网点", "理财推荐", "查询账单"]
    }


# 处理用户消息
@app.post("/message", response_model=MessageResponse)
def handle_message(request: MessageRequest, db: Session = Depends(get_db)):
    # 分析用户意图
    intent = analyze_intent(request.message)
    
    # 生成回复，传递用户上下文
    response = generate_response(request.message, intent, request.username, db, user_context)
    
    return response


# 获取理财产品详情
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="理财产品不存在")
    
    return product


# 获取网点详情
@app.get("/branches/{branch_id}", response_model=BranchResponse)
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="网点不存在")
    
    return branch
