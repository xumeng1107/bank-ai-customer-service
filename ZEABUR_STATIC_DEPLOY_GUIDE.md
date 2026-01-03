# Zeabur静态前端部署指南

本指南将帮助您将银行智能客服前端部署到Zeabur静态网站服务。

## 部署方案

您有两种方式获得完整的前端体验：

### 方案A：独立静态网站部署（推荐）

1. **上传静态前端代码**
   - 使用`static-frontend`目录中的文件
   - 该目录包含完整的静态前端配置

2. **部署步骤**
   ```
   1. 登录Zeabur控制台
   2. 选择"静态网站"类型
   3. 上传static-frontend目录
   4. 配置服务端口：8080
   5. 部署完成后获得域名
   ```

3. **优势**
   - 完整的聊天界面体验
   - 自动环境检测
   - 与后端API同域集成

### 方案B：后端项目中集成静态服务

1. **修改main.py添加静态文件服务**
   ```python
   from fastapi.staticfiles import StaticFiles
   from fastapi.responses import FileResponse
   
   # 添加静态文件服务
   app.mount("/", StaticFiles(directory=".", html=True), name="static")
   ```

2. **部署优势**
   - 单一服务
   - 自动CORS处理
   - 简化部署流程

## 快速部署方案A

### 步骤1：准备静态文件
```bash
# static-frontend目录已准备完成，包含：
# - index.html（前端界面）
# - zeabur.json（部署配置）
# - README.md（使用说明）
```

### 步骤2：部署到Zeabur
1. 访问 [Zeabur控制台](https://zeabur.com)
2. 点击"New Project"
3. 选择"Static Site"
4. 上传`static-frontend`目录
5. 配置启动命令：`npx serve -s . -l 8080`
6. 点击部署

### 步骤3：验证部署
访问部署后的域名，应该看到：
- 银行智能客服登录界面
- 完整的聊天功能
- 响应式设计

## 环境配置说明

### 前端API自动配置
前端代码包含智能环境检测：

```javascript
const isLocalDev = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1';

if (isLocalDev) {
    API_URL = 'http://127.0.0.1:8000';  // 本地开发
} else {
    API_URL = window.location.origin;    // 生产环境
}
```

### 跨域配置
后端已配置CORS支持：
- 开发环境：允许所有来源
- 生产环境：可通过`FRONTEND_URL`环境变量配置

## 部署后测试

部署完成后，请测试以下功能：

1. **基本访问**：确认前端页面正常加载
2. **登录功能**：点击登录按钮
3. **聊天功能**：发送测试消息
4. **API连接**：检查网络请求是否成功

## 故障排除

### 问题1：前端页面404
**解决方案**：检查`index.html`是否在正确位置

### 问题2：API请求失败
**解决方案**：
1. 确认后端服务正常运行
2. 检查CORS配置
3. 验证API URL配置

### 问题3：样式显示异常
**解决方案**：检查CSS文件路径和加载

## 完整部署流程

1. **后端部署**（已完成）
   - 将`main.py`等项目文件部署到Zeabur
   - 监听8080端口
   - 配置环境变量

2. **前端部署**（本指南）
   - 使用`static-frontend`目录
   - 部署为静态网站
   - 监听8080端口

3. **最终效果**
   - 访问前端域名看到完整聊天界面
   - 前端自动连接到后端API
   - 享受完整的银行智能客服体验

---

**注意**：确保前后端部署在同一个域名或配置适当的CORS设置。