# 银行AI客服系统

一个基于FastAPI后端和Vue.js前端的智能银行客服系统。

## 功能特性

- 🔐 用户登录验证
- 🤖 智能意图识别
- 💰 理财产品推荐
- 🏢 网点查询服务
- 📊 账单查询分析
- 💡 智能对话交互

## 技术栈

### 后端
- **FastAPI** - 高性能Python Web框架
- **SQLAlchemy** - 数据库ORM
- **SQLite** - 轻量级数据库
- **DashScope SDK** - 通义千问LLM集成

### 前端
- **HTML5** - 响应式界面
- **CSS3** - 现代样式设计
- **JavaScript** - 交互逻辑
- **Fetch API** - 后端通信

## 项目结构

```
├── main.py              # FastAPI应用主文件
├── qwen.py             # LLM集成和业务逻辑
├── models.py           # 数据库模型
├── schemas.py          # Pydantic数据验证
├── config.py           # 配置文件
├── database.py         # 数据库连接
├── index.html          # 前端界面
├── requirements.txt    # Python依赖
├── test/               # 测试脚本目录
│   ├── test_all_features.py
│   ├── test_finance_context.py
│   ├── test_hangzhou_branches.py
│   ├── test_intent.py
│   ├── test_recommend_finance.py
│   └── test_specific_query.py
└── zeabur.json         # Zeabur部署配置
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 14+ (可选)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动后端服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端服务

```bash
python -m http.server 3000
```

### 运行测试

```bash
cd test
python test_*.py
```

## 访问地址

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 部署

支持部署到以下平台：
- **Zeabur** (推荐)
- **Railway**
- **Heroku**
- **AWS/GCP/阿里云**

## 许可证

MIT License

## 作者

xm18091582523@163.com

## 贡献

欢迎提交Issue和Pull Request！
