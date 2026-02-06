"""
配置管理模块
负责应用配置的读写和凭证的安全存储
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict
from cryptography.fernet import Fernet


class ConfigManager:
    """配置管理器（支持加密存储）"""

    def __init__(self):
        """初始化配置管理器"""
        self.config_dir = Path.home() / ".yibo_client"
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / "key.bin"

        # 创建配置目录
        self.config_dir.mkdir(exist_ok=True)

        # 初始化加密密钥
        self._init_encryption()

    def _init_encryption(self):
        """初始化加密密钥"""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)

        key = self.key_file.read_bytes()
        self.cipher = Fernet(key)

    def save_credentials(self, server: str, username: str, password: str, auto_login: bool = False):
        """保存凭证（密码加密存储）

        Args:
            server: 服务器地址
            username: 用户名
            password: 密码
            auto_login: 是否自动登录
        """
        config = {
            'server': server,
            'username': username,
            'password': self.cipher.encrypt(password.encode()).decode(),
            'auto_login': auto_login
        }

        self.config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    def load_credentials(self) -> Optional[Dict[str, str]]:
        """加载凭证

        Returns:
            包含 server, username, password, auto_login 的字典，如果不存在则返回 None
        """
        if not self.config_file.exists():
            return None

        try:
            config = json.loads(self.config_file.read_text(encoding='utf-8'))

            # 解密密码
            if 'password' in config:
                encrypted_pwd = config['password'].encode()
                config['password'] = self.cipher.decrypt(encrypted_pwd).decode()

            return config
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None

    def clear_credentials(self):
        """清除凭证"""
        if self.config_file.exists():
            self.config_file.unlink()

    def get_last_server(self) -> str:
        """获取上次使用的服务器地址"""
        cred = self.load_credentials()
        return cred.get('server', '') if cred else ''

    def get_last_username(self) -> str:
        """获取上次使用的用户名"""
        cred = self.load_credentials()
        return cred.get('username', '') if cred else ''
