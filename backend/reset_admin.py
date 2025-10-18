#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""重置所有测试用户密码脚本"""

from app import app, db, User

def reset_all_passwords():
    """重置所有测试用户密码"""
    with app.app_context():
        # 定义测试账号
        test_users = [
            {'username': 'admin', 'password': 'admin123', 'real_name': '系统管理员', 'role': 'admin'},
            {'username': 'zhangsan', 'password': 'user123', 'real_name': '张三', 'role': 'user', 'email': 'zhangsan@example.com'},
            {'username': 'lisi', 'password': 'user123', 'real_name': '李四', 'role': 'user', 'email': 'lisi@example.com'},
        ]
        
        print("\n正在重置所有测试用户密码...\n")
        
        for user_data in test_users:
            user = User.query.filter_by(username=user_data['username']).first()
            
            if user:
                # 用户存在，更新密码
                user.set_password(user_data['password'])
                print(f"[√] {user_data['username']} - 密码已重置")
            else:
                # 用户不存在，创建新用户
                user = User(
                    username=user_data['username'],
                    real_name=user_data['real_name'],
                    role=user_data['role'],
                    email=user_data.get('email'),
                    total_points=0,
                    available_points=0
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"[√] {user_data['username']} - 账号已创建")
        
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("所有测试账号密码已重置：")
        print("=" * 50)
        print("\n【管理员】")
        print("  用户名: admin")
        print("  密码: admin123")
        print("\n【普通用户1】")
        print("  用户名: zhangsan")
        print("  密码: user123")
        print("\n【普通用户2】")
        print("  用户名: lisi")
        print("  密码: user123")
        print("\n" + "=" * 50)
        print("[√] 完成！现在可以使用这些账号登录了")

if __name__ == '__main__':
    print("=" * 50)
    print("重置所有测试用户密码")
    print("=" * 50)
    
    try:
        reset_all_passwords()
    except Exception as e:
        print(f"\n[×] 错误: {e}")
        print("\n请确保：")
        print("1. 数据库连接配置正确")
        print("2. thumbs_mall 数据库已创建")
        print("3. users 表已创建")

