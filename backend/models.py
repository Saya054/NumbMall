from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum('admin', 'user'), default='user')
    total_points = db.Column(db.Integer, default=0)
    available_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    thumbs_records = db.relationship('ThumbsRecord', foreign_keys='ThumbsRecord.user_id', backref='user', lazy='dynamic')
    exchange_records = db.relationship('ExchangeRecord', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'total_points': self.total_points,
            'available_points': self.available_points,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class ThumbsRecord(db.Model):
    """大拇哥记录模型"""
    __tablename__ = 'thumbs_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thumb_type = db.Column(db.Enum('single', 'double'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))
    given_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    giver = db.relationship('User', foreign_keys=[given_by])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else None,
            'thumb_type': self.thumb_type,
            'thumb_type_name': '单大拇哥👍' if self.thumb_type == 'single' else '双大拇哥👍👍',
            'points': self.points,
            'reason': self.reason,
            'given_by': self.given_by,
            'given_by_name': self.giver.real_name if self.giver else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Product(db.Model):
    """商品模型"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    points_required = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('on_shelf', 'off_shelf'), default='off_shelf')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    exchange_records = db.relationship('ExchangeRecord', backref='product', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'points_required': self.points_required,
            'stock': self.stock,
            'status': self.status,
            'status_name': '已上架' if self.status == 'on_shelf' else '已下架',
            'sort_order': self.sort_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class ExchangeRecord(db.Model):
    """兑换记录模型"""
    __tablename__ = 'exchange_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    points_spent = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.Enum('pending', 'completed', 'cancelled'), default='pending')
    remark = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else None,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'points_spent': self.points_spent,
            'quantity': self.quantity,
            'status': self.status,
            'status_name': {'pending': '待处理', 'completed': '已完成', 'cancelled': '已取消'}.get(self.status),
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }



