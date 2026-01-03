import dashscope
from config import settings
from sqlalchemy.orm import Session
from models import User, Account, Branch, Bill, Product

# 初始化通义千问API密钥
dashscope.api_key = settings.API_KEY


def analyze_intent(message: str) -> str:
    """分析用户意图"""
    # 使用通义千问进行意图识别，更灵活的提示词
    response = dashscope.Generation.call(
        model="qwen-turbo",
        prompt=f"""你是一个银行智能客服系统，请分析用户的输入，识别其核心意图。
用户可能的意图包括：
1. 账户查询：查询账户余额、账户信息等
2. 网点查询：查询附近银行网点、网点地址、营业时间等
3. 账单查询：查询账单明细、收支情况、月度/年度账单等
4. 理财查询：查询理财产品、理财推荐、理财详情等
5. 业务流程查询：查询业务办理流程、所需资料等
6. 其他：无法归类到上述意图的其他请求

请严格按照上述意图列表返回唯一的意图名称，不要添加任何解释或额外内容。

用户输入：{message}
""",
        temperature=0.1
    )
    
    if response.status_code == 200:
        intent = response.output.text.strip()
        # 确保返回的意图在预定义列表中
        valid_intents = ["账户查询", "网点查询", "账单查询", "理财查询", "业务流程查询", "其他"]
        if intent in valid_intents:
            return intent
        else:
            # 处理可能的意图映射，例如用户可能说"我想理财"，模型可能返回"理财查询"
            return "其他"
    
    # 默认返回其他
    return "其他"


def generate_response(message: str, intent: str, username: str, db: Session, user_context: dict) -> dict:
    """生成回复内容，由通义千问大模型主导信息判断和内容筛选"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return {
            "message": "用户不存在，请先登录",
            "suggestions": []
        }
    
    # 获取用户相关信息
    account = db.query(Account).filter(Account.user_id == user.id).first()
    products = db.query(Product).all()
    branches = db.query(Branch).all()
    
    # 准备系统提示词
    system_prompt = f"""你是一个专业的银行智能客服，名叫小银，现在正在与用户{user.name}对话。
请用友好、专业的语气回答用户的问题，保持简洁明了，不要使用过于 technical 的术语。

你可以使用以下用户信息和银行数据来回答问题：

1. 用户信息：
   - 用户名：{user.username}
   - 姓名：{user.name}
   - 账户信息：{'有账户，余额：' + str(account.balance) + '元，类型：' + account.account_type if account else '暂无账户'}

2. 银行理财产品（共{len(products)}款）：
{chr(10).join([f'   - {p.name}：{p.description}，风险等级：{p.risk_level}，起购金额：{p.min_amount}元，年化收益率：{p.annual_rate}%' for p in products])}

3. 银行网点信息（共{len(branches)}个）：
{chr(10).join([f'   - {b.name}：地址：{b.address}，电话：{b.phone}，营业时间：{b.hours}' for b in branches])}

请根据用户的问题，结合以上信息，生成友好、专业的回复。
如果用户询问理财产品，请根据用户情况推荐合适的产品，并说明推荐理由。
如果用户查询账户，请提供准确的账户信息。
如果用户查询网点，请提供相关网点信息。
如果用户查询账单，请询问具体的月份或年份。
如果用户需要理财推荐，请根据用户的账户余额或假设余额推荐合适的产品。

请使用中文回答，保持简洁明了，不要使用过于 technical 的术语。
"""
    
    # 调用通义千问大模型
    qwen_response = dashscope.Generation.call(
        model="qwen-turbo",
        prompt=f"{system_prompt}\n\n用户问题：{message}",
        temperature=0.7
    )
    
    # 处理大模型回复
    if qwen_response.status_code == 200:
        message_content = qwen_response.output.text.strip()
    else:
        message_content = "抱歉，我暂时无法回答您的问题，请稍后重试。"
    
    # 生成响应
    recommended_products = None
    has_more_products = False
    
    # 处理网点查询逻辑 - 先检查消息是否包含城市信息
    if (intent == "网点查询" or "网点" in message or "地址" in message or 
        "杭州" in message or "我在杭州" in message or "北京" in message or "我在北京" in message):
        # 只显示前3个网点
        recommended_products = None
        has_more_products = False
        
        # 初始化用户上下文
        if username not in user_context:
            user_context[username] = {
                "city": None,
                "financial_query": {
                    "keywords": [],
                    "rate": None,
                    "rate_condition": None,
                    "amount": None,
                    "amount_condition": None,
                    "risk": None
                }
            }
        
        # 检测用户所在城市
        # 优先使用上下文中的城市
        city = user_context[username]["city"]
        # 如果上下文中没有城市，或者消息中明确提到城市，则更新城市
        if city is None or "杭州" in message or "我在杭州" in message or "北京" in message or "我在北京" in message:
            if "杭州" in message or "我在杭州" in message:
                city = "杭州"
            else:
                city = "北京"  # 默认城市
            # 更新上下文
            user_context[username]["city"] = city
        
        # 根据城市筛选网点
        city_branches = [branch for branch in branches if city in branch.address]
        
        # 限制网点数量为3个
        if len(city_branches) > 3:
            display_branches = city_branches[:3]
        else:
            display_branches = city_branches
        
        # 生成网点查询的特定回复
        message_content = f"{user.name}您好！我们的银行网点主要位于北京和杭州，以下是{city}的几个网点信息："
        
        response = {
            "message": message_content,
            "suggestions": ["查询账户余额", "查询账单", "需要理财推荐"],
            "products": None,
            "has_more_products": False,
            "branches": display_branches
        }
        return response
    
    # 处理账单查询逻辑
    elif intent == "账单查询" or "账单" in message:
        # 提取月份或年份或月份范围
        import re
        month_match = re.search(r'(20\d{2})[-年](0?[1-9]|1[0-2])', message)
        year_match = re.search(r'(20\d{2})', message)
        
        # 新增：提取月份范围，例如"2024年1月到2月"或"2024年1月至2月"，允许连接词和月份之间有空格
        month_range_match = re.search(r'(20\d{2})[-年](0?[1-9]|1[0-2])(?:月)?\s*(到|至)\s*(20\d{2})?[-年]?(0?[1-9]|1[0-2])(?:月)?', message)
        
        # 检查是否需要账单明细
        need_detail = any(keyword in message for keyword in ["明细", "详细", "详情"])
        
        user_bills = db.query(Bill).filter(Bill.user_id == user.id).all()
        
        # 新增：处理月份范围查询
        if month_range_match:
            # 提取起始年份、起始月份、结束年份、结束月份
            start_year = month_range_match.group(1)
            start_month = month_range_match.group(2).zfill(2)
            end_year = month_range_match.group(4) if month_range_match.group(4) else start_year  # 如果没有指定结束年份，使用起始年份
            end_month = month_range_match.group(5).zfill(2)
            
            # 构造起始和结束月份的字符串格式
            start_month_str = f"{start_year}-{start_month}"
            end_month_str = f"{end_year}-{end_month}"
            
            # 筛选在范围内的账单
            range_bills = [bill for bill in user_bills if start_month_str <= bill.month <= end_month_str]
            
            if range_bills:
                # 计算总收支
                total_income = sum(bill.income for bill in range_bills)
                total_expense = sum(bill.expense for bill in range_bills)
                
                # 构造账单详情
                bill_details = []
                for bill in sorted(range_bills, key=lambda x: x.month):
                    bill_year, bill_month = bill.month.split('-')
                    bill_details.append(f"{bill_year}年{bill_month}月：收入{bill.income}元，支出{bill.expense}元，结余{bill.income - bill.expense}元")
                
                message_content = f"{user.name}您好！您{start_year}年{start_month}月到{end_year}年{end_month}月的账单信息如下：\n" + "\n".join(bill_details) + f"\n\n总览：\n总收入：{total_income}元\n总支出：{total_expense}元\n总结余：{total_income - total_expense}元"
            else:
                message_content = f"{user.name}您好！未找到您{start_year}年{start_month}月到{end_year}年{end_month}月的账单信息。"
        elif month_match:
            # 精确到月份查询
            year = month_match.group(1)
            month = month_match.group(2).zfill(2)
            target_month = f"{year}-{month}"
            
            bill = next((b for b in user_bills if b.month == target_month), None)
            if bill:
                if need_detail:
                    # 返回详细账单内容
                    message_content = f"{user.name}您好！您{year}年{month}月的详细账单如下：\n\n{bill.description}\n收入：{bill.income}元\n支出：{bill.expense}元\n结余：{bill.income - bill.expense}元\n\n如需查询其他月份的账单，请提供具体的月份和年份。"
                else:
                    message_content = f"{user.name}您好！您{year}年{month}月的账单信息如下：\n收入：{bill.income}元\n支出：{bill.expense}元\n结余：{bill.income - bill.expense}元"
            else:
                message_content = f"{user.name}您好！未找到您{year}年{month}月的账单信息。"
        elif year_match:
            # 按年份查询
            year = year_match.group(1)
            year_bills = [b for b in user_bills if b.month.startswith(year)]
            
            if year_bills:
                total_income = sum(b.income for b in year_bills)
                total_expense = sum(b.expense for b in year_bills)
                
                if need_detail:
                    # 返回该年份所有月份的详细账单
                    bill_details = []
                    for bill in sorted(year_bills, key=lambda x: x.month):
                        y, m = bill.month.split('-')
                        bill_details.append(f"{y}年{m}月：\n{bill.description}\n收入：{bill.income}元\n支出：{bill.expense}元\n结余：{bill.income - bill.expense}元\n")
                    message_content = f"{user.name}您好！您{year}年的详细账单汇总如下：\n\n" + "\n".join(bill_details) + f"\n年度总收入：{total_income}元\n年度总支出：{total_expense}元\n年度总结余：{total_income - total_expense}元"
                else:
                    message_content = f"{user.name}您好！您{year}年的账单汇总如下：\n总收入：{total_income}元\n总支出：{total_expense}元\n总结余：{total_income - total_expense}元\n共查询到{len(year_bills)}个月的账单数据。"
            else:
                message_content = f"{user.name}您好！未找到您{year}年的账单信息。"
        else:
            # 没有指定月份或年份，返回最近3个月的账单
            recent_bills = sorted(user_bills, key=lambda x: x.month, reverse=True)[:3]
            if recent_bills:
                bill_details = []
                for bill in recent_bills:
                    year, month = bill.month.split('-')
                    bill_details.append(f"{year}年{month}月：收入{bill.income}元，支出{bill.expense}元，结余{bill.income - bill.expense}元")
                message_content = f"{user.name}您好！这是您最近3个月的账单信息：\n" + "\n".join(bill_details) + "\n\n如需查询具体月份的详细账单，请提供具体的月份和年份。"
            else:
                message_content = f"{user.name}您好！未找到您的账单信息。"
        
        response = {
            "message": message_content,
            "suggestions": ["查询账户余额", "查询网点", "需要理财推荐"],
            "products": None,
            "has_more_products": False,
            "branches": None
        }
        return response
    

    
    # 处理产品推荐逻辑
    elif "理财" in message or "产品" in message or "年化" in message or "起购" in message or "风险" in message or "收益" in message or "推荐" in message:
        # 初始化用户上下文
        if username not in user_context:
            user_context[username] = {
                "city": None,
                "financial_query": {
                    "keywords": [],
                    "rate": None,
                    "rate_condition": None,
                    "amount": None,
                    "amount_condition": None,
                    "risk": None
                }
            }
        
        # 从当前消息中提取理财查询的条件
        import re
        # 只提取真正的关键字，不包括风险等级，风险等级单独处理
        current_keywords = re.findall(r'(灵活|定期|保本|成长|科技|创业)', message)
        
        # 提取年化收益率要求
        # 改进正则表达式，支持比较词在%之后，如'年化3%以上'
        rate_pattern = re.compile(r'(年化|收益率|收益).*?(\d+(?:\.\d+)?)%.*?(超过|高于|大于|低于|小于|为|是|以上|以下)?')
        rate_match = rate_pattern.search(message)
        current_rate_condition = None
        current_target_rate = None
        
        if rate_match:
            current_target_rate = float(rate_match.group(2))
            # 获取比较条件，先检查匹配的比较词，再检查消息中是否包含其他比较词
            compare_word = rate_match.group(3)
            # 映射比较词
            compare_mapping = {
                "超过": "gt",
                "高于": "gt",
                "大于": "gt",
                "以上": "gt",
                "低于": "lt",
                "小于": "lt",
                "以下": "lt",
                "为": "eq",
                "是": "eq"
            }
            
            if compare_word:
                current_rate_condition = compare_mapping.get(compare_word, "eq")
            else:
                # 检查消息中是否有其他比较词
                if any(word in message for word in ["超过", "高于", "大于", "以上"]):
                    current_rate_condition = "gt"  # 大于
                elif any(word in message for word in ["低于", "小于", "以下"]):
                    current_rate_condition = "lt"  # 小于
                else:
                    current_rate_condition = "eq"  # 等于（默认）
        
        # 提取起购金额要求
        amount_pattern = re.compile(r'(起购|购买|门槛).*?(大于|小于|高于|低于|超过|为|是)?.*?(\d+(?:\.\d+)?)')
        amount_match = amount_pattern.search(message)
        
        # 提取用户投资金额
        investment_amount_match = re.search(r'(拿|用|投资|理财)(\d+(?:\.\d+)?)[块钱]', message)
        
        current_amount_condition = None
        current_target_amount = None
        investment_amount = None
        
        if amount_match:
            current_target_amount = float(amount_match.group(3))
            # 检查是否有比较条件
            # 从正则匹配中提取比较词
            compare_word = amount_match.group(2)
            if compare_word:
                if compare_word in ["超过", "高于", "大于"]:
                    current_amount_condition = "gt"  # 大于
                elif compare_word in ["低于", "小于"]:
                    current_amount_condition = "lt"  # 小于
                else:
                    current_amount_condition = "eq"  # 等于
            else:
                # 如果没有提取到比较词，检查整个消息
                if "超过" in message or "高于" in message or "大于" in message:
                    current_amount_condition = "gt"  # 大于
                elif "低于" in message or "小于" in message:
                    current_amount_condition = "lt"  # 小于
                else:
                    current_amount_condition = "eq"  # 等于（默认）
        
        # 提取用户投资金额
        if investment_amount_match:
            investment_amount = float(investment_amount_match.group(2))
        
        # 提取风险等级要求
        risk_match = re.search(r'风险等级(?:为|是)?(低风险|中风险|高风险)', message)
        current_target_risk = None
        
        # 首先检查消息中是否包含风险等级关键字
        # 映射风险等级名称到数据库中的缩写
        risk_mapping = {
            "低风险": "低",
            "中风险": "中",
            "高风险": "高"
        }
        
        current_target_risk = None
        if any(word in message for word in ["低风险", "低"]):
            current_target_risk = "低"
        elif any(word in message for word in ["中风险", "中"]):
            current_target_risk = "中"
        elif any(word in message for word in ["高风险", "高"]):
            current_target_risk = "高"
        elif risk_match:
            # 从匹配结果中提取风险等级并映射
            match_risk = risk_match.group(1)
            current_target_risk = risk_mapping.get(match_risk, match_risk)
        
        # 去掉上下文关联，每次理财查询都是独立的
        # 只使用当前消息中的查询条件
        
        # 关键字：只使用当前消息中的关键字
        keywords = current_keywords
        
        # 年化收益率：只使用当前消息中的年化收益率要求
        target_rate = current_target_rate
        rate_condition = current_rate_condition
        
        # 起购金额：只使用当前消息中的起购金额要求
        target_amount = current_target_amount
        amount_condition = current_amount_condition
        
        # 风险等级：只使用当前消息中的风险等级要求
        target_risk = current_target_risk
        
        # 重置理财查询上下文，确保每次查询都是独立的
        user_context[username]["financial_query"] = {
            "keywords": [],
            "rate": None,
            "rate_condition": None,
            "amount": None,
            "amount_condition": None,
            "risk": None
        }
        
        # 如果是查看更多请求，保留之前的筛选逻辑，但确保页码正确
        is_load_more = "查看更多" in message
        
        # 筛选产品
        filtered_products = []
        
        # 检查是否有任何筛选条件
        has_filter_conditions = (len(keywords) > 0 or 
                                target_rate is not None or 
                                target_amount is not None or 
                                target_risk is not None or 
                                investment_amount is not None)
        
        # 调试信息
        print(f"Debug: has_filter_conditions={has_filter_conditions}, keywords={keywords}, target_rate={target_rate}, target_amount={target_amount}, target_risk={target_risk}, investment_amount={investment_amount}")
        
        if not has_filter_conditions:
            # 如果没有任何筛选条件，直接返回所有产品
            filtered_products = products
        else:
            # 否则按照条件筛选产品
            for product in products:
                # 检查关键字匹配
                keyword_match = not keywords or any(keyword in product.description or keyword in product.name for keyword in keywords)
                
                # 检查年化收益率匹配
                rate_ok = True
                if target_rate is not None:
                    if rate_condition == "gt":
                        rate_ok = product.annual_rate > target_rate
                    elif rate_condition == "lt":
                        rate_ok = product.annual_rate < target_rate
                    else:
                        rate_ok = abs(product.annual_rate - target_rate) <= 0.5  # 允许±0.5%的误差
                
                # 检查起购金额匹配
                amount_ok = True
                if target_amount is not None:
                    if amount_condition == "gt":
                        amount_ok = product.min_amount > target_amount
                    elif amount_condition == "lt":
                        amount_ok = product.min_amount < target_amount
                    else:
                        amount_ok = product.min_amount == target_amount
                # 如果用户指定了投资金额，确保产品起购金额小于等于投资金额
                if investment_amount is not None:
                    amount_ok = amount_ok and product.min_amount <= investment_amount
                
                # 检查风险等级匹配
                risk_ok = True
                if target_risk is not None:
                    risk_ok = product.risk_level == target_risk
                
                # 如果同时满足所有条件，添加到筛选结果
                if keyword_match and rate_ok and amount_ok and risk_ok:
                    filtered_products.append(product)
        
        # 提取当前页码或起始位置
        page_match = re.search(r'查看更多(\d+)', message)
        start_index = 0
        page_size = 3
        
        # 检查是否有匹配的产品
        if not filtered_products:
            # 没有找到合适的产品
            message_content = f"{user.name}您好！根据您的所有要求，没有合适的产品。"
            recommended_products = None
            has_more_products = False
        elif page_match:
            # 查看更多请求，计算起始位置
            current_page = int(page_match.group(1))
            start_index = current_page * page_size
            
            # 分页处理
            recommended_products = filtered_products[start_index:start_index+page_size]
            has_more_products = len(filtered_products) > start_index + page_size
            
            if not recommended_products:
                # 没有更多产品
                message_content = f"{user.name}您好！目前没有更多的理财产品。"
                recommended_products = None
                has_more_products = False
            else:
                # 查看更多请求，继续推荐3个同类型产品
                message_content = f"{user.name}您好！为您继续推荐以下{len(recommended_products)}款理财产品："
        elif "查看所有" in message or "全部" in message:
            # 返回所有筛选后的产品
            recommended_products = filtered_products
            has_more_products = False
            message_content = f"{user.name}您好！为您推荐以下{len(recommended_products)}款理财产品："
        else:
            # 初始请求，从第0页开始
            start_index = 0
            
            # 分页处理
            recommended_products = filtered_products[start_index:start_index+page_size]
            has_more_products = len(filtered_products) > start_index + page_size
            
            # 初始请求
            message_content = f"{user.name}您好！为您推荐以下{len(recommended_products)}款理财产品："
    
    # 动态生成建议按钮，根据当前查询内容调整
    base_suggestions = ["查询账户余额", "查询网点", "查询账单", "需要理财推荐"]
    
    # 如果用户已经查询了账户，去掉"查询账户余额"选项
    if intent == "账户查询" or "账户" in message:
        suggestions = [s for s in base_suggestions if s != "查询账户余额"]
    # # 如果用户已经查询了网点，去掉"查询网点"选项
    if intent == "网点查询" or "网点" in message:
        suggestions = [s for s in base_suggestions if s != "查询网点"]
    # 如果用户已经查询了账单，去掉"查询账单"选项
    elif intent == "账单查询" or "账单" in message:
        suggestions = [s for s in base_suggestions if s != "查询账单"]
    # 如果用户已经查询了理财，去掉"需要理财推荐"选项
    elif intent == "理财查询" or "理财" in message or "产品" in message:
        suggestions = [s for s in base_suggestions if s != "需要理财推荐"]
    else:
        suggestions = base_suggestions
    
    response = {
        "message": message_content,
        "suggestions": suggestions,
        "products": recommended_products,
        "has_more_products": has_more_products,
        "branches": branches if "网点" in message or "地址" in message else None
    }
    
    return response
