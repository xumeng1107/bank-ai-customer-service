import requests

# 测试'给我推荐理财'功能
API_URL = 'http://127.0.0.1:8000'

def test_recommend_finance():
    print("测试'给我推荐理财'功能...")
    
    # 首先登录
    login_response = requests.post(f'{API_URL}/login/test')
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        return
    
    login_data = login_response.json()
    print(f"登录成功，欢迎: {login_data['user']['name']}")
    
    # 发送'给我推荐理财'消息
    message_response = requests.post(f'{API_URL}/message', json={
        'message': '给我推荐理财',
        'username': 'test'
    })
    
    if message_response.status_code != 200:
        print(f"消息发送失败: {message_response.status_code}")
        return
    
    message_data = message_response.json()
    print(f"\n响应状态: 成功")
    print(f"响应消息: {message_data['message']}")
    print(f"是否包含products: {'products' in message_data}")
    if 'products' in message_data and message_data['products']:
        print(f"返回产品数量: {len(message_data['products'])}")
        for product in message_data['products']:
            print(f"  - {product['name']}")
    else:
        print("未返回产品信息！")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_recommend_finance()
