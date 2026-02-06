"""
配置管理器单元测试
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from src.utils.config_manager import ConfigManager


class TestConfigManager:
    """测试配置管理器"""

    def setup_method(self):
        """每个测试前的准备"""
        # 使用临时目录进行测试
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = ConfigManager()
        # 替换为临时目录
        self.config_manager.config_dir = self.temp_dir
        self.config_manager.config_file = self.temp_dir / "config.json"
        self.config_manager.key_file = self.temp_dir / "key.bin"
        self.config_manager._init_encryption()

    def teardown_method(self):
        """每个测试后的清理"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_save_and_load_credentials(self):
        """测试凭证保存和加载"""
        # 保存凭证
        self.config_manager.save_credentials(
            server="https://test.com",
            username="admin",
            password="secret123",
            auto_login=True
        )

        # 加载凭证
        cred = self.config_manager.load_credentials()

        assert cred is not None
        assert cred['server'] == "https://test.com"
        assert cred['username'] == "admin"
        assert cred['password'] == "secret123"
        assert cred['auto_login'] is True

    def test_password_encryption(self):
        """测试密码加密存储"""
        original_password = "my_secret_password"

        # 保存凭证
        self.config_manager.save_credentials(
            server="https://test.com",
            username="user",
            password=original_password
        )

        # 直接读取配置文件（不解密）
        import json
        raw_config = json.loads(self.config_manager.config_file.read_text())

        # 确认密码已加密（不等于原始密码）
        assert raw_config['password'] != original_password

        # 但通过 load_credentials 可以正确解密
        cred = self.config_manager.load_credentials()
        assert cred['password'] == original_password

    def test_clear_credentials(self):
        """测试清除凭证"""
        # 保存凭证
        self.config_manager.save_credentials(
            server="https://test.com",
            username="admin",
            password="pass123"
        )

        # 清除凭证
        self.config_manager.clear_credentials()

        # 确认文件已删除
        assert not self.config_manager.config_file.exists()

        # 加载返回 None
        cred = self.config_manager.load_credentials()
        assert cred is None

    def test_get_last_server(self):
        """测试获取上次服务器地址"""
        # 未保存时返回空字符串
        assert self.config_manager.get_last_server() == ''

        # 保存后返回正确值
        self.config_manager.save_credentials(
            server="https://example.com",
            username="user",
            password="pass"
        )
        assert self.config_manager.get_last_server() == "https://example.com"

    def test_get_last_username(self):
        """测试获取上次用户名"""
        # 未保存时返回空字符串
        assert self.config_manager.get_last_username() == ''

        # 保存后返回正确值
        self.config_manager.save_credentials(
            server="https://example.com",
            username="testuser",
            password="pass"
        )
        assert self.config_manager.get_last_username() == "testuser"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
