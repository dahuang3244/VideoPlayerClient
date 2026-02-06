"""
认证服务集成测试
"""
import pytest
from unittest.mock import Mock, patch
from src.network.auth_service import AuthService, AuthResult


class TestAuthService:
    """测试认证服务"""

    @patch('requests.Session.get')
    def test_login_success(self, mock_get):
        """测试登录成功场景"""
        # Mock 成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 200,
            'message': 'Login successful',
            'data': {
                'token': 'test_token_12345',
                'expire': 7200,
                'username': '10001'
            }
        }
        mock_get.return_value = mock_response

        # 执行登录
        service = AuthService("https://test.com")
        result = service.login("admin", "password")

        # 验证结果
        assert result.success is True
        assert result.token == 'test_token_12345'
        assert result.expire == 7200
        assert result.user_id == '10001'

    @patch('requests.Session.get')
    def test_login_wrong_password(self, mock_get):
        """测试密码错误"""
        mock_response = Mock()
        mock_response.status_code = 200  # 通常 API 会返回 200 OK，但在 body 里返回错误码，或者直接 HTTP 403
        # 根据文档：HTTP 状态行始终为 HTTP/1.1 [status] OK (文档表述有歧义，但示例显示 403 OK)
        # 文档: "HTTP/1.1 403 OK" -> status: 403
        # requests.status_code 会是 403

        mock_response.status_code = 403
        mock_response.json.return_value = {
            'status': 403,
            'message': 'Invalid signature' # 或者是密码错误相关的
        }
        mock_get.return_value = mock_response

        service = AuthService("https://test.com")
        result = service.login("admin", "wrong_password")

        assert result.success is False
        assert result.error_code == 403

    @patch('requests.Session.get')
    def test_login_user_not_found(self, mock_get):
        """测试用户不存在"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'status': 404,
            'message': 'User not found'
        }
        mock_get.return_value = mock_response

        service = AuthService("https://test.com")
        result = service.login("nonexistent", "password")

        assert result.success is False
        assert "User not found" in result.error_msg

    @patch('requests.Session.get')
    def test_login_network_timeout(self, mock_get):
        """测试网络超时"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        service = AuthService("https://test.com")
        result = service.login("admin", "password")

        assert result.success is False
        assert "超时" in result.error_msg

    @patch('requests.Session.get')
    def test_login_ssl_error(self, mock_get):
        """测试 SSL 错误"""
        import requests
        mock_get.side_effect = requests.exceptions.SSLError()

        service = AuthService("https://test.com")
        result = service.login("admin", "password")

        assert result.success is False
        assert "SSL" in result.error_msg


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
