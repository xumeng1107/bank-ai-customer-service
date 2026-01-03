# GitHub仓库创建指南

## 步骤1: 在GitHub上创建新仓库

1. 访问 https://github.com
2. 登录您的GitHub账户
3. 点击右上角的 "+" 按钮，选择 "New repository"
4. 填写仓库信息：
   - **Repository name**: `bank-ai-customer-service`
   - **Description**: `银行AI客服系统 - 基于FastAPI和Vue.js的智能客服解决方案`
   - **Visibility**: 选择 "Public" 或 "Private"
   - **DO NOT** 勾选 "Add a README file"（我们已经有了）
   - **DO NOT** 勾选 "Add .gitignore"（我们已经有了）
   - **DO NOT** 勾选 "Choose a license"（可选）

5. 点击 "Create repository"

## 步骤2: 推送代码到GitHub

创建仓库后，GitHub会显示一个页面，其中有推送指令。请执行以下命令：

```bash
git remote set-url origin https://github.com/xm18091582523/bank-ai-customer-service.git
git branch -M main
git push -u origin main
```

## 步骤3: 验证推送

推送成功后，您的代码将出现在GitHub仓库中。

## 访问您的仓库

您的GitHub仓库地址将是：
https://github.com/xm18091582523/bank-ai-customer-service

## 注意事项

- 确保您的GitHub账户已验证邮箱
- 如果遇到认证问题，可能需要设置GitHub Personal Access Token
- 仓库创建完成后，推送应该会成功

## 下一步

推送成功后，您可以：
1. 在GitHub上查看您的代码
2. 邀请其他开发者参与项目
3. 设置GitHub Pages（如果需要）
4. 配置CI/CD流水线
5. 添加项目徽章和统计数据

