#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
大拇哥积分商城 - 统一管理工具
基于 PyQt5 的图形化管理界面
"""

import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QGroupBox, QTabWidget,
    QLineEdit, QMessageBox, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon


class WorkerThread(QThread):
    """后台工作线程"""
    output = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self, command, cwd=None):
        super().__init__()
        self.command = command
        self.cwd = cwd or os.path.dirname(__file__)
    
    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.cwd,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            for line in process.stdout:
                self.output.emit(line.strip())
            
            process.wait()
            self.finished.emit(process.returncode == 0)
        except Exception as e:
            self.output.emit(f"错误: {str(e)}")
            self.finished.emit(False)


class ManageTool(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker = None
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('大拇哥积分商城 - 管理工具')
        self.setGeometry(100, 100, 900, 700)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 标题
        title = QLabel('👍 大拇哥积分商城管理工具')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 选项卡
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # 各个选项卡
        tabs.addTab(self.create_env_tab(), '环境检查')
        tabs.addTab(self.create_database_tab(), '数据库管理')
        tabs.addTab(self.create_server_tab(), '服务管理')
        tabs.addTab(self.create_config_tab(), '配置管理')
        
        # 输出区域
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(200)
        layout.addWidget(QLabel('操作日志：'))
        layout.addWidget(self.output_text)
        
        # 状态栏
        self.statusBar().showMessage('就绪')
    
    def create_env_tab(self):
        """环境检查选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 检查按钮
        btn_layout = QHBoxLayout()
        
        btn_check_python = QPushButton('检查 Python')
        btn_check_python.clicked.connect(lambda: self.run_command('python --version', '检查 Python'))
        btn_layout.addWidget(btn_check_python)
        
        btn_check_node = QPushButton('检查 Node.js')
        btn_check_node.clicked.connect(lambda: self.run_command('node --version', '检查 Node.js'))
        btn_layout.addWidget(btn_check_node)
        
        btn_check_mysql = QPushButton('检查 MySQL')
        btn_check_mysql.clicked.connect(lambda: self.run_command('mysql --version', '检查 MySQL'))
        btn_layout.addWidget(btn_check_mysql)
        
        layout.addLayout(btn_layout)
        
        # 安装依赖
        group = QGroupBox('安装依赖')
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)
        
        btn_install_backend = QPushButton('安装后端依赖')
        btn_install_backend.clicked.connect(self.install_backend_deps)
        group_layout.addWidget(btn_install_backend)
        
        btn_install_frontend = QPushButton('安装前端依赖')
        btn_install_frontend.clicked.connect(self.install_frontend_deps)
        group_layout.addWidget(btn_install_frontend)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return widget
    
    def create_database_tab(self):
        """数据库管理选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 数据库密码输入
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel('MySQL密码:'))
        self.mysql_password = QLineEdit()
        self.mysql_password.setEchoMode(QLineEdit.Password)
        pwd_layout.addWidget(self.mysql_password)
        layout.addLayout(pwd_layout)
        
        # 数据库操作
        btn_init_db = QPushButton('初始化数据库')
        btn_init_db.clicked.connect(self.init_database)
        layout.addWidget(btn_init_db)
        
        btn_reset_passwords = QPushButton('重置所有测试用户密码')
        btn_reset_passwords.clicked.connect(self.reset_test_passwords)
        layout.addWidget(btn_reset_passwords)
        
        # 说明
        info = QLabel(
            '说明：\n'
            '• 初始化数据库：创建数据库和表，导入测试数据\n'
            '• 重置密码：将 admin、zhangsan、lisi 的密码重置为默认值'
        )
        info.setStyleSheet('color: #666; padding: 10px; background: #f5f5f5; border-radius: 5px;')
        layout.addWidget(info)
        
        layout.addStretch()
        return widget
    
    def create_server_tab(self):
        """服务管理选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 后端服务
        backend_group = QGroupBox('后端服务')
        backend_layout = QVBoxLayout()
        backend_group.setLayout(backend_layout)
        
        btn_start_backend = QPushButton('启动后端服务')
        btn_start_backend.clicked.connect(self.start_backend)
        backend_layout.addWidget(btn_start_backend)
        
        layout.addWidget(backend_group)
        
        # 前端服务
        frontend_group = QGroupBox('前端服务')
        frontend_layout = QVBoxLayout()
        frontend_group.setLayout(frontend_layout)
        
        btn_start_frontend = QPushButton('启动前端服务')
        btn_start_frontend.clicked.connect(self.start_frontend)
        frontend_layout.addWidget(btn_start_frontend)
        
        layout.addWidget(frontend_group)
        
        # 说明
        info = QLabel(
            '说明：\n'
            '• 启动服务会打开新的命令行窗口\n'
            '• 后端地址: http://localhost:5000\n'
            '• 前端地址: http://localhost:5173\n'
            '• 关闭窗口即可停止服务'
        )
        info.setStyleSheet('color: #666; padding: 10px; background: #f5f5f5; border-radius: 5px;')
        layout.addWidget(info)
        
        layout.addStretch()
        return widget
    
    def create_config_tab(self):
        """配置管理选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 配置数据库密码
        group = QGroupBox('配置数据库密码')
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)
        
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel('MySQL密码:'))
        self.config_mysql_pwd = QLineEdit()
        self.config_mysql_pwd.setEchoMode(QLineEdit.Password)
        pwd_layout.addWidget(self.config_mysql_pwd)
        group_layout.addLayout(pwd_layout)
        
        btn_save_config = QPushButton('保存配置')
        btn_save_config.clicked.connect(self.save_config)
        group_layout.addWidget(btn_save_config)
        
        layout.addWidget(group)
        
        # 说明
        info = QLabel(
            '说明：\n'
            '• 配置会保存到 backend/.env 文件\n'
            '• 保存后需要重启后端服务才能生效'
        )
        info.setStyleSheet('color: #666; padding: 10px; background: #f5f5f5; border-radius: 5px;')
        layout.addWidget(info)
        
        layout.addStretch()
        return widget
    
    def log(self, message):
        """添加日志"""
        self.output_text.append(message)
        self.output_text.ensureCursorVisible()
    
    def run_command(self, command, description):
        """运行命令"""
        self.log(f'\n>>> {description}')
        self.log(f'执行: {command}\n')
        
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, '警告', '有任务正在执行，请稍候')
            return
        
        self.worker = WorkerThread(command)
        self.worker.output.connect(self.log)
        self.worker.finished.connect(lambda success: self.on_task_finished(success, description))
        self.worker.start()
        
        self.statusBar().showMessage(f'执行中: {description}')
    
    def on_task_finished(self, success, description):
        """任务完成"""
        if success:
            self.log(f'\n✓ {description} 完成')
            self.statusBar().showMessage(f'{description} 完成')
        else:
            self.log(f'\n× {description} 失败')
            self.statusBar().showMessage(f'{description} 失败')
    
    def install_backend_deps(self):
        """安装后端依赖"""
        command = 'pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple'
        self.run_command(command, '安装后端依赖')
    
    def install_frontend_deps(self):
        """安装前端依赖"""
        command = 'cd frontend && npm install --registry=https://registry.npmmirror.com'
        self.run_command(command, '安装前端依赖')
    
    def init_database(self):
        """初始化数据库"""
        password = self.mysql_password.text()
        if not password:
            QMessageBox.warning(self, '警告', '请输入MySQL密码')
            return
        
        # 这里需要手动执行
        QMessageBox.information(
            self, '提示',
            '请在命令行执行:\n\n'
            f'mysql -u root -p < database\\init.sql\n\n'
            '然后输入密码完成初始化'
        )
    
    def reset_test_passwords(self):
        """重置测试用户密码"""
        command = 'cd backend && python reset_admin.py'
        self.run_command(command, '重置测试用户密码')
    
    def start_backend(self):
        """启动后端"""
        subprocess.Popen('start cmd /k "cd backend && python app.py"', shell=True)
        self.log('\n后端服务已在新窗口启动')
        self.statusBar().showMessage('后端服务已启动')
    
    def start_frontend(self):
        """启动前端"""
        subprocess.Popen('start cmd /k "cd frontend && npm run dev"', shell=True)
        self.log('\n前端服务已在新窗口启动')
        self.statusBar().showMessage('前端服务已启动')
    
    def save_config(self):
        """保存配置"""
        password = self.config_mysql_pwd.text()
        if not password:
            QMessageBox.warning(self, '警告', '请输入MySQL密码')
            return
        
        env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f'MYSQL_HOST=localhost\n')
                f.write(f'MYSQL_PORT=3306\n')
                f.write(f'MYSQL_USER=root\n')
                f.write(f'MYSQL_PASSWORD={password}\n')
                f.write(f'MYSQL_DATABASE=thumbs_mall\n\n')
                f.write(f'SECRET_KEY=your-secret-key-change-in-production\n')
                f.write(f'JWT_SECRET_KEY=jwt-secret-key-change-in-production\n')
            
            self.log('\n✓ 配置已保存到 backend/.env')
            QMessageBox.information(self, '成功', '配置已保存！\n请重启后端服务使配置生效。')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存配置失败: {str(e)}')


def main():
    app = QApplication(sys.argv)
    window = ManageTool()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



