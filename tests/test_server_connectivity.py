
import sys
import os

# 将 src 目录添加到路径中以便导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.network.auth_service import AuthService

def test_connection():
    server_url = "http://47.109.184.107:8080"
    username = "test_user"
    password = "test_password"
    
    print(f"正在尝试连接服务器: {server_url}")
    auth_service = AuthService(server_url, timeout=30)
    
    try:
        result = auth_service.login(username, password)
        
        print("\n--- 测试结果 ---")
        print(f"请求成功: {result.success}")
        if result.success:
            print(f"Token: {result.token}")
            print(f"UserID: {result.user_id}")
        else:
            print(f"错误码: {result.error_code}")
            print(f"错误信息: {result.error_msg}")
            
    except Exception as e:
        print(f"发生异常: {e}")

if __name__ == "__main__":
    test_connection()
