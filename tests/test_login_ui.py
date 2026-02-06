"""
登录表单手动测试脚本
运行此脚本可以打开登录窗口进行手动测试
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.login_form import LoginForm


def main():
    """启动登录窗口"""
    app = QApplication(sys.argv)

    # 创建登录窗口
    login_form = LoginForm()

    # 连接成功信号
    def on_login_success(token, user_id):
        QMessageBox.information(
            None,
            "登录成功",
            f"Token: {token[:30]}...\nUser ID: {user_id}"
        )
        print(f"\n✅ 登录成功！")
        print(f"Token: {token}")
        print(f"User ID: {user_id}")

    login_form.login_success.connect(on_login_success)

    # 显示窗口
    login_form.show()

    print("\n" + "=" * 60)
    print("登录窗口测试")
    print("=" * 60)
    print("\n请在窗口中输入以下测试信息：")
    print("  服务器: https://your-server.com")
    print("  用户名: admin")
    print("  密码: password123")
    print("\n注意：")
    print("  1. 如果服务器不可用，会显示连接错误")
    print("  2. 可以勾选'记住密码'测试配置保存功能")
    print("  3. 支持回车键快速登录")
    print("=" * 60 + "\n")

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
