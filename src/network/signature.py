"""
签名生成器模块
实现 HTTP 认证协议的 MD5 签名算法
"""
import hashlib
import time
import random
import string
from typing import Dict


class SignatureGenerator:
    """MD5 签名生成器（静态工具类）"""

    @staticmethod
    def generate_salt(length: int = 10) -> str:
        """生成随机盐值

        Args:
            length: 盐值长度（默认10位）

        Returns:
            随机字符串（包含字母和数字）
        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def calculate_signature(user: str, timestamp: int, password: str, salt: str) -> str:
        """计算 MD5 签名

        签名算法：MD5(user + timestamp + password + salt)

        Args:
            user: 用户名
            timestamp: Unix 时间戳（秒级）
            password: 用户密码（明文）
            salt: 随机盐值

        Returns:
            32 位小写 MD5 哈希值

        Example:
            >>> sig = SignatureGenerator.calculate_signature('admin', 1738742400, 'pass123', 'abc')
            >>> len(sig)
            32
        """
        # 拼接字符串（严格按照协议顺序）
        raw_string = f"{user}{timestamp}{password}{salt}"

        # 计算 MD5
        md5_hash = hashlib.md5(raw_string.encode('utf-8')).hexdigest()

        return md5_hash.lower()

    @staticmethod
    def build_auth_params(username: str, password: str) -> Dict[str, str]:
        """构建完整的认证请求参数

        Args:
            username: 用户名
            password: 密码

        Returns:
            包含 user, time, salt, sign 的字典

        Example:
            >>> params = SignatureGenerator.build_auth_params('admin', 'pass123')
            >>> 'sign' in params
            True
            >>> len(params['sign'])
            32
        """
        timestamp = int(time.time())
        salt = SignatureGenerator.generate_salt()
        signature = SignatureGenerator.calculate_signature(
            username, timestamp, password, salt
        )

        return {
            'user': username,
            'time': str(timestamp),
            'salt': salt,
            'sign': signature
        }
