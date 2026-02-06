"""
HTTP 认证服务模块
负责与服务器进行认证交互
"""
import requests
from typing import Optional
from dataclasses import dataclass
from .signature import SignatureGenerator


@dataclass
class AuthResult:
    """认证结果数据类"""
    success: bool
    token: Optional[str] = None
    expire: int = 0
    user_id: Optional[str] = None
    error_msg: Optional[str] = None
    error_code: int = 0


class AuthService:
    """HTTP 认证服务"""

    def __init__(self, server_url: str, timeout: int = 10):
        """初始化认证服务

        Args:
            server_url: 服务器地址（如 https://server.com）
            timeout: 请求超时时间（秒）
        """
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'YiBoClient/1.0',
            'Connection': 'close'
        })

    def login(self, username: str, password: str) -> AuthResult:
        """执行登录认证

        Args:
            username: 用户名
            password: 密码

        Returns:
            AuthResult 对象
        """
        try:
            # 1. 构造签名参数
            params = SignatureGenerator.build_auth_params(username, password)

            # 2. 发送请求 (路径修正为 /login)
            url = f"{self.server_url}/login"
            print(f"[DEBUG] Sending request to: {url} with params: {params}")
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            print(f"[DEBUG] Response received: {response.status_code}")


            # 3. 解析响应 (统一检查 JSON 中的 status)
            try:
                data = response.json()
            except ValueError:
                return AuthResult(
                    success=False,
                    error_msg=f"无法解析服务器返回内容 (HTTP {response.status_code})"
                )

            status = data.get('status')
            message = data.get('message', '未知错误')

            if status == 200:
                res_data = data.get('data', {})
                return AuthResult(
                    success=True,
                    token=res_data.get('token', ''), # 源码可能尚未下发 token，但文档预留了 data 结构
                    expire=res_data.get('expire', 7200),
                    user_id=res_data.get('username', username)
                )
            else:
                return AuthResult(
                    success=False,
                    error_msg=message,
                    error_code=status if isinstance(status, int) else response.status_code
                )

        except requests.exceptions.Timeout:
            return AuthResult(success=False, error_msg="连接超时，请检查网络")

        except requests.exceptions.SSLError:
            return AuthResult(success=False, error_msg="SSL 证书验证失败")

        except requests.exceptions.ConnectionError:
            return AuthResult(
                success=False,
                error_msg=f"无法连接到服务器：{self.server_url}"
            )

        except Exception as e:
            return AuthResult(success=False, error_msg=f"未知错误: {str(e)}")

    def set_ssl_verify(self, verify: bool):
        """设置 SSL 证书验证（仅用于开发环境）

        Args:
            verify: 是否验证 SSL 证书
        """
        self.session.verify = verify
