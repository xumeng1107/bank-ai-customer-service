import requests

# 测试特定查询'给我推荐几个风险等级中，年化3%以上的产品'
API_URL = 'http://127.0.0.1:8000'

def test_specific_query():
    print("测试'给我推荐几个风险等级中，年化3%以上的产品'...")
    
    # 首先登录
    login_response = requests.post(f'{API_URL}/login/test')
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        return
    
    login_data = login_response.json()
    print(f"登录成功，欢迎: {login_data['user']['name']}")
    
    # 发送特定查询消息
    message_response = requests.post(f'{API_URL}/message', json={
        'message': '给我推荐几个风险等级中，年化3%以上的产品',
        'username': 'test'
    })
    
    if message_response.status_code != 200:
        print(f"消息发送失败: {message_response.status_code}")
        return
    
    message_data = message_response.json()
    print(f"\n响应状态: 成功")
    print(f"响应消息: {message_data['message']}")
    print(f"是否包含products: {'products' in message_data}")
    if 'products' in message_data and message_data['products'] is not None:
        print(f"返回产品数量: {len(message_data['products'])}")
        for product in message_data['products']:
            print(f"  - {product['name']}: 风险等级{product['risk_level']}，年化{product['annual_rate']}%")
    else:
        print("返回产品信息: None")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_specific_query()
