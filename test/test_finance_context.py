import requests

# 测试连续理财查询的上下文管理
API_URL = 'http://127.0.0.1:8000'

def test_finance_context():
    print("=== 测试连续理财查询的上下文管理 ===")
    
    # 首先登录
    login_response = requests.post(f'{API_URL}/login/test')
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        return
    
    login_data = login_response.json()
    print(f"登录成功，欢迎: {login_data['user']['name']}")
    
    # 测试1: 给我推荐理财
    print("\n测试1: 给我推荐理财")
    message1_response = requests.post(f'{API_URL}/message', json={
        'message': '给我推荐理财',
        'username': 'test'
    })
    message1_data = message1_response.json()
    print(f"响应消息: {message1_data['message'][:50]}...")
    print(f"是否包含products: {'products' in message1_data}")
    if 'products' in message1_data and message1_data['products']:
        print(f"返回产品数量: {len(message1_data['products'])}")
    
    # 测试2: 低风险的
    print("\n测试2: 低风险的")
    message2_response = requests.post(f'{API_URL}/message', json={
        'message': '低风险的',
        'username': 'test'
    })
    message2_data = message2_response.json()
    print(f"响应消息: {message2_data['message'][:50]}...")
    print(f"是否包含products: {'products' in message2_data}")
    if 'products' in message2_data and message2_data['products']:
        print(f"返回产品数量: {len(message2_data['products'])}")
    
    # 测试3: 年化超过3%
    print("\n测试3: 年化超过3%")
    message3_response = requests.post(f'{API_URL}/message', json={
        'message': '年化超过3%',
        'username': 'test'
    })
    message3_data = message3_response.json()
    print(f"响应消息: {message3_data['message'][:50]}...")
    print(f"是否包含products: {'products' in message3_data}")
    if 'products' in message3_data and message3_data['products']:
        print(f"返回产品数量: {len(message3_data['products'])}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_finance_context()
