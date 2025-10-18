#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的密码重置脚本
直接连接数据库，不依赖 Flask app
"""

import pymysql
from werkzeug.security import generate_password_hash

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Xy20190411',  # 修改为你的 MySQL 密码
    'database': 'thumbs_mall',
    'charset': 'utf8mb4'
}

# 测试用户配置
TEST_USERS = [
    {'username': 'admin', 'password': 'admin123', 'real_name': '系统管理员', 'role': 'admin'},
    {'username': 'zhangsan', 'password': 'user123', 'real_name': '张三', 'role': 'user'},
    {'username': 'lisi', 'password': 'user123', 'real_name': '李四', 'role': 'user'},
]

def reset_passwords():
    """重置密码"""
    print("=" * 60)
    print("大拇哥积分商城 - 重置测试用户密码")
    print("=" * 60)
    print()
    
    try:
        # 连接数据库
        print("[*] 正在连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("[√] 数据库连接成功")
        print()
        
        print("[*] 正在重置密码...")
        print()
        
        for user_data in TEST_USERS:
            username = user_data['username']
            password = user_data['password']
            real_name = user_data['real_name']
            role = user_data['role']
            
            # 生成密码哈希
            password_hash = generate_password_hash(password)
            
            # 检查用户是否存在
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if result:
                # 用户存在，更新密码
                cursor.execute(
                    "UPDATE users SET password = %s WHERE username = %s",
                    (password_hash, username)
                )
                print(f"[√] {username:10s} - 密码已重置为: {password}")
            else:
                # 用户不存在，创建新用户
                cursor.execute(
                    """INSERT INTO users (username, password, real_name, role, total_points, available_points)
                       VALUES (%s, %s, %s, %s, 0, 0)""",
                    (username, password_hash, real_name, role)
                )
                print(f"[√] {username:10s} - 账号已创建，密码: {password}")
        
        # 提交更改
        conn.commit()
        
        print()
        print("=" * 60)
        print("所有测试账号密码已重置成功！")
        print("=" * 60)
        print()
        print("【管理员】")
        print("  用户名: admin")
        print("  密码: admin123")
        print()
        print("【普通用户1】")
        print("  用户名: zhangsan")
        print("  密码: user123")
        print()
        print("【普通用户2】")
        print("  用户名: lisi")
        print("  密码: user123")
        print()
        print("=" * 60)
        print("[√] 完成！现在可以使用这些账号登录了")
        print()
        
        # 关闭连接
        cursor.close()
        conn.close()
        
    except pymysql.err.OperationalError as e:
        print()
        print(f"[×] 数据库连接失败: {e}")
        print()
        print("请检查：")
        print("1. MySQL 服务是否启动")
        print("2. 数据库密码是否正确（修改本文件第12行）")
        print("3. 数据库 thumbs_mall 是否已创建")
        print()
        
    except Exception as e:
        print()
        print(f"[×] 错误: {e}")
        print()

if __name__ == '__main__':
    reset_passwords()
    input("\n按回车键退出...")

