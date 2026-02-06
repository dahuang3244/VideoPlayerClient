"""
登录窗口模块
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from network.auth_service import AuthService, AuthResult
from utils.config_manager import ConfigManager


class AuthThread(QThread):
    """认证线程（避免阻塞UI）"""
    finished = pyqtSignal(AuthResult)

    def __init__(self, service: AuthService, username: str, password: str):
        super().__init__()
        self.service = service
        self.username = username
        self.password = password

    def run(self):
        """执行认证"""
        result = self.service.login(self.username, self.password)
        self.finished.emit(result)


class LoginForm(QWidget):
    """登录窗口"""

    login_success = pyqtSignal(str, str)  # 发射 (token, user_id)

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.auth_thread = None
        self.init_ui()
        self.load_saved_config()

    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("易播客户端 - 登录")
        self.setFixedSize(450, 320)

        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        title = QLabel("易播客户端")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 服务器地址
        server_layout = QHBoxLayout()
        server_label = QLabel("服务器:")
        server_label.setFixedWidth(70)
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("http://47.109.184.107:8080")
        self.server_input.setText("http://47.109.184.107:8080") # 默认填入真实服务器地址
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_input)
        layout.addLayout(server_layout)

        # 用户名
        user_layout = QHBoxLayout()
        user_label = QLabel("用户名:")
        user_label.setFixedWidth(70)
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("请输入用户名")
        self.user_input.setText("admin") # 默认用户名
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)
        layout.addLayout(user_layout)

        # 密码
        pwd_layout = QHBoxLayout()
        pwd_label = QLabel("密码:")
        pwd_label.setFixedWidth(70)
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("请输入密码")
        pwd_layout.addWidget(pwd_label)
        pwd_layout.addWidget(self.pwd_input)
        layout.addLayout(pwd_layout)

        # 记住密码
        self.remember_checkbox = QCheckBox("记住密码")
        layout.addWidget(self.remember_checkbox)

        # 自动登录
        self.auto_login_checkbox = QCheckBox("自动登录")
        layout.addWidget(self.auto_login_checkbox)

        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.clicked.connect(self.on_login_clicked)
        layout.addWidget(self.login_btn)

        # 支持回车键登录
        self.pwd_input.returnPressed.connect(self.on_login_clicked)

        self.setLayout(layout)

    def load_saved_config(self):
        """加载保存的配置"""
        cred = self.config_manager.load_credentials()
        if cred:
            self.server_input.setText(cred.get('server', ''))
            self.user_input.setText(cred.get('username', ''))
            if cred.get('auto_login', False):
                self.pwd_input.setText(cred.get('password', ''))
                self.remember_checkbox.setChecked(True)
                self.auto_login_checkbox.setChecked(True)

    def validate_inputs(self) -> tuple[bool, str]:
        """验证输入合法性

        Returns:
            (是否通过, 错误提示)
        """
        server = self.server_input.text().strip()
        user = self.user_input.text().strip()
        pwd = self.pwd_input.text()

        if not server:
            return False, "请输入服务器地址"

        if not server.startswith(('http://', 'https://')):
            return False, "服务器地址必须以 http:// 或 https:// 开头"

        if not user:
            return False, "请输入用户名"

        if len(user) < 2:
            return False, "用户名至少 2 个字符"

        if not pwd:
            return False, "请输入密码"

        if len(pwd) < 4:
            return False, "密码至少 4 个字符"

        return True, ""

    def on_login_clicked(self):
        """处理登录按钮点击"""
        # 1. 验证输入
        valid, error_msg = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "输入错误", error_msg)
            return

        # 2. 进入加载状态
        self.set_loading(True)

        # 3. 在子线程执行认证
        auth_service = AuthService(self.server_input.text())

        # 开发环境：暂时跳过 SSL 验证
        if self.server_input.text().startswith('http://'):
            auth_service.set_ssl_verify(False)

        self.auth_thread = AuthThread(
            auth_service,
            self.user_input.text(),
            self.pwd_input.text()
        )
        self.auth_thread.finished.connect(self.on_auth_finished)
        self.auth_thread.start()

    def set_loading(self, loading: bool):
        """设置加载状态"""
        self.login_btn.setEnabled(not loading)
        self.user_input.setEnabled(not loading)
        self.pwd_input.setEnabled(not loading)
        self.server_input.setEnabled(not loading)
        self.remember_checkbox.setEnabled(not loading)
        self.auto_login_checkbox.setEnabled(not loading)

        if loading:
            self.login_btn.setText("登录中...")
        else:
            self.login_btn.setText("登录")

    def on_auth_finished(self, result: AuthResult):
        """认证完成回调"""
        self.set_loading(False)

        if result.success:
            # 保存配置
            if self.remember_checkbox.isChecked():
                self.config_manager.save_credentials(
                    self.server_input.text(),
                    self.user_input.text(),
                    self.pwd_input.text(),
                    self.auto_login_checkbox.isChecked()
                )

            # 发射成功信号
            self.login_success.emit(result.token, result.user_id)
            QMessageBox.information(self, "登录成功", f"欢迎，用户ID: {result.user_id}")
            self.close()
        else:
            QMessageBox.critical(self, "登录失败", result.error_msg)
            # 清空密码框
            self.pwd_input.clear()
            self.pwd_input.setFocus()


# 测试代码
if __name__ == '__main__':
    app = QApplication(sys.argv)

    login_form = LoginForm()

    def on_success(token, user_id):
        print(f"登录成功！Token: {token[:20]}..., UserID: {user_id}")

    login_form.login_success.connect(on_success)
    login_form.show()

    sys.exit(app.exec())
