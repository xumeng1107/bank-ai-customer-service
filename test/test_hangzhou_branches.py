import requests

# 测试用户输入"我在杭州"时的响应
API_URL = 'http://127.0.0.1:8000'

def test_hangzhou_branches():
    print("测试用户输入'我在杭州'的响应...")
    
    # 首先登录获取用户名
    login_response = requests.post(f'{API_URL}/login/test')
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        return
    
    login_data = login_response.json()
    print(f"登录成功，欢迎: {login_data['user']['name']}")
    
    # 发送"我在杭州"的消息
    message_response = requests.post(f'{API_URL}/message', json={
        'message': '我在杭州',
        'username': 'test'
    })
    
    if message_response.status_code != 200:
        print(f"消息发送失败: {message_response.status_code}")
        return
    
    message_data = message_response.json()
    print(f"\n响应状态: 成功")
    print(f"响应消息: {message_data['message']}")
    print(f"是否包含suggestions: {'suggestions' in message_data}")
    print(f"是否包含branches: {'branches' in message_data}")
    
    if 'branches' in message_data and message_data['branches']:
        print(f"\n返回的杭州网点数量: {len(message_data['branches'])}")
        print("网点信息:")
        for branch in message_data['branches']:
            print(f"  - {branch['name']}: {branch['address']}, {branch['phone']}")
    else:
        print("\n未返回杭州网点信息！")
    
    print("\n测试完成")

if __name__ == "__main__":
    test_hangzhou_branches()
