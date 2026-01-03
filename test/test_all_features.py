import requests

# 测试所有功能是否正常工作
API_URL = 'http://127.0.0.1:8000'

def test_all_features():
    print("=== 测试1：修改文案为'查询网点' ===")
    login_response = requests.post(f'{API_URL}/login/test')
    login_data = login_response.json()
    print(f"登录成功，欢迎: {login_data['user']['name']}")
    print(f"初始化建议按钮: {login_data['suggestions']}")
    
    print("\n=== 测试2：上下文管理 - 杭州网点查询 ===")
    # 测试用户输入"我在杭州"，然后输入"查询网点"
    message1_response = requests.post(f'{API_URL}/message', json={
        'message': '我在杭州',
        'username': 'test'
    })
    message1_data = message1_response.json()
    print(f"'我在杭州'响应包含branches: {'branches' in message1_data}")
    if 'branches' in message1_data and message1_data['branches']:
        print(f"返回杭州网点数量: {len(message1_data['branches'])}")
        print(f"第一个网点城市: {'杭州' in message1_data['branches'][0]['address']}")
    
    print("\n输入'查询网点'")
    message2_response = requests.post(f'{API_URL}/message', json={
        'message': '查询网点',
        'username': 'test'
    })
    message2_data = message2_response.json()
    print(f"'查询网点'响应包含branches: {'branches' in message2_data}")
    if 'branches' in message2_data and message2_data['branches']:
        print(f"返回网点数量: {len(message2_data['branches'])}")
        print(f"网点城市: {'杭州' in message2_data['branches'][0]['address']}")
    
    print("\n=== 测试3：理财查询上下文管理 ===")
    # 测试连续输入理财查询
    print("输入'起购大于100'")
    message3_response = requests.post(f'{API_URL}/message', json={
        'message': '起购大于100',
        'username': 'test'
    })
    message3_data = message3_response.json()
    print(f"响应消息: {message3_data['message'][:100]}...")
    
    print("\n输入'年化超过5%'")
    message4_response = requests.post(f'{API_URL}/message', json={
        'message': '年化超过5%',
        'username': 'test'
    })
    message4_data = message4_response.json()
    print(f"响应消息: {message4_data['message'][:100]}...")
    
    print("\n=== 测试4：无合适理财产品返回 ===")
    # 测试无法匹配的理财要求
    print("输入'起购大于100000，年化超过20%'")
    message5_response = requests.post(f'{API_URL}/message', json={
        'message': '起购大于100000，年化超过20%',
        'username': 'test'
    })
    message5_data = message5_response.json()
    print(f"响应消息: {message5_data['message']}")
    print(f"是否包含'没有合适的产品': {'没有合适的产品' in message5_data['message']}")
    
    print("\n=== 所有测试完成 ===")

if __name__ == "__main__":
    test_all_features()
