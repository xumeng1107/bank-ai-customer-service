# Zeabur部署指南

本指南将帮助您成功在Zeabur上部署银行智能客服系统。

## 🚀 快速部署步骤

### 1. 环境变量配置
在Zeabur控制台中设置以下环境变量：

**必需环境变量：**
```
DASHSCOPE_API_KEY=您的DashScope API密钥
DATABASE_PATH=sqlite:///tmp/bank.db
```

**可选环境变量：**
```
FRONTEND_URL=*
```

### 2. 部署步骤
1. 登录 [Zeabur控制台](https://zeabur.com)
2. 点击 "New Project"
3. 选择 "Connect GitHub" 或 "Deploy from URL"
4. 选择您的银行智能客服仓库
5. 设置环境变量（见上方配置）
6. 点击 "Deploy"

### 3. 部署验证
部署完成后，访问您的域名：
- **前端界面**：`https://您的域名.zeabur.app`
- **API文档**：`https://您的域名.zeabur.app/docs`

## 🔧 故障排除

### 问题1：数据库连接失败
**错误信息**：`sqlite3.OperationalError: unable to open database file`

**解决方案**：
- 确保设置了 `DATABASE_PATH=sqlite:///tmp/bank.db`
- 验证环境变量是否正确设置

### 问题2：API密钥错误
**错误信息**：`DASHSCOPE_API_KEY environment variable not set`

**解决方案**：
- 检查 `DASHSCOPE_API_KEY` 环境变量是否设置
- 验证API密钥是否有效

### 问题3：服务启动失败
**解决方案**：
1. 检查启动日志
2. 确认所有依赖项正确安装
3. 验证端口配置（默认8080）

## 📋 环境变量详解

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DASHSCOPE_API_KEY` | ✅ | 无 | DashScope API密钥，用于AI服务 |
| `DATABASE_PATH` | ❌ | `sqlite:///tmp/bank.db` | 数据库文件路径，容器环境推荐使用/tmp |
| `FRONTEND_URL` | ❌ | `*` | 前端域名，CORS配置用 |

## 🏗️ 架构说明

### 前后端一体化部署
- **根路径 `/`**：返回前端HTML页面
- **API路径 `/api/**`：提供后端服务
- **静态资源 `/static/**`：提供前端静态文件

### 数据库配置
- **本地开发**：使用相对路径 `./bank.db`
- **容器部署**：使用绝对路径 `/tmp/bank.db`
- **自定义**：通过 `DATABASE_PATH` 环境变量配置

## 🔍 调试指南

### 查看启动日志
1. 在Zeabur控制台中进入您的项目
2. 点击 "Logs" 标签页
3. 查看启动日志和错误信息

### 常见日志信息
```
使用容器环境数据库路径: /tmp/bank.db
数据库表创建成功
数据库已存在数据，跳过初始化
开始初始化模拟数据...
```

### 测试API端点
```bash
# 测试根路径
curl https://您的域名.zeabur.app/

# 测试登录API
curl -X POST https://您的域名.zeabur.app/login/test

# 测试消息API
curl -X POST https://您的域名.zeabur.app/message \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "message": "你好"}'
```

## 📊 性能优化

### 数据库优化
- 在生产环境中考虑使用PostgreSQL
- 对于高并发场景，使用连接池

### 前端优化
- 启用静态文件缓存
- 压缩HTML、CSS、JavaScript

## 🛡️ 安全建议

1. **API密钥安全**
   - 不要在代码中硬编码API密钥
   - 定期轮换API密钥

2. **CORS配置**
   - 生产环境中设置具体的FRONTEND_URL
   - 避免使用通配符 `*`

3. **数据库安全**
   - 定期备份数据库文件
   - 考虑使用加密数据库

## 📞 支持

如果遇到部署问题，请：
1. 检查上述故障排除指南
2. 查看Zeabur控制台日志
3. 确认环境变量配置正确

---

**部署成功后，您将获得一个完全功能的银行智能客服系统！** 🎉