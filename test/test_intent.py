import dashscope
from config import settings

# 初始化通义千问API密钥
dashscope.api_key = settings.API_KEY

def test_intent_analysis():
    print("测试'我在杭州'的意图识别...")
    
    # 调用通义千问进行意图识别
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

用户输入：我在杭州
""",
        temperature=0.1
    )
    
    if response.status_code == 200:
        intent = response.output.text.strip()
        print(f"识别的意图: '{intent}'")
        print(f"是否为网点查询: {intent == '网点查询'}")
    else:
        print(f"意图识别失败: {response.status_code}")

if __name__ == "__main__":
    test_intent_analysis()
