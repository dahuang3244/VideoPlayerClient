"""
签名生成器单元测试
"""
import pytest
import hashlib
from src.network.signature import SignatureGenerator


class TestSignatureGenerator:
    """测试签名生成器"""

    def test_calculate_signature_correctness(self):
        """测试签名计算的正确性"""
        user = "admin"
        timestamp = 1738742400
        password = "123456"
        salt = "abc123"

        # 预期签名
        raw_string = f"{user}{timestamp}{password}{salt}"
        expected = hashlib.md5(raw_string.encode()).hexdigest()

        # 实际签名
        actual = SignatureGenerator.calculate_signature(user, timestamp, password, salt)

        assert actual == expected
        assert len(actual) == 32
        assert actual.islower()  # 必须是小写

    def test_salt_generation(self):
        """测试盐值生成"""
        salt1 = SignatureGenerator.generate_salt()
        salt2 = SignatureGenerator.generate_salt()

        # 长度检查
        assert len(salt1) == 10
        assert len(salt2) == 10

        # 随机性检查
        assert salt1 != salt2

        # 字符集检查
        assert salt1.isalnum()

    def test_build_auth_params(self):
        """测试参数构建"""
        params = SignatureGenerator.build_auth_params("testuser", "testpwd")

        # 必须包含所有字段
        assert 'user' in params
        assert 'time' in params
        assert 'salt' in params
        assert 'sign' in params

        # 类型检查
        assert params['user'] == 'testuser'
        assert len(params['sign']) == 32
        assert params['time'].isdigit()

    def test_signature_with_special_characters(self):
        """测试特殊字符处理"""
        user = "user@test.com"
        password = "p@ss!word#123"
        timestamp = 1234567890
        salt = "xyz"

        # 不应该抛出异常
        sign = SignatureGenerator.calculate_signature(user, timestamp, password, salt)
        assert len(sign) == 32


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
