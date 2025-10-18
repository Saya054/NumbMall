from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid
from config import Config
from models import db, User, ThumbsRecord, Product, ExchangeRecord

app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# 创建上传目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== 文件上传 API ====================

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '没有文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'code': 400, 'message': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # 保存文件
        file.save(filepath)
        
        # 返回文件URL
        file_url = f"/api/uploads/{filename}"
        
        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'url': file_url,
                'filename': filename
            }
        })
    
    return jsonify({'code': 400, 'message': '不支持的文件类型'}), 400


@app.route('/api/uploads/<filename>')
def get_upload_file(filename):
    """获取上传的文件"""
    return send_from_directory(UPLOAD_FOLDER, filename)


# ==================== 认证相关 API ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': access_token,
            'user': user.to_dict()
        }
    })


@app.route('/api/auth/info', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    return jsonify({
        'code': 200,
        'data': user.to_dict()
    })


@app.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改当前用户密码"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'code': 400, 'message': '旧密码和新密码不能为空'}), 400
    
    # 验证旧密码
    if not user.check_password(old_password):
        return jsonify({'code': 400, 'message': '旧密码错误'}), 400
    
    # 设置新密码
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '密码修改成功'
    })


@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    real_name = data.get('real_name')
    email = data.get('email')
    phone = data.get('phone')
    
    if not username or not password or not real_name:
        return jsonify({'code': 400, 'message': '用户名、密码和姓名不能为空'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400
    
    # 创建新用户
    user = User(
        username=username,
        real_name=real_name,
        email=email,
        phone=phone,
        role='user',
        total_points=0,
        available_points=0
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': user.to_dict()
    })


# ==================== 用户管理 API ====================

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    
    query = User.query
    if keyword:
        query = query.filter(
            db.or_(
                User.username.like(f'%{keyword}%'),
                User.real_name.like(f'%{keyword}%')
            )
        )
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'data': {
            'list': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@app.route('/api/users', methods=['POST'])
@jwt_required()
def create_user():
    """创建用户"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限操作'}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    real_name = data.get('real_name')
    
    if not username or not password or not real_name:
        return jsonify({'code': 400, 'message': '必填字段不能为空'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400
    
    user = User(
        username=username,
        real_name=real_name,
        email=data.get('email'),
        phone=data.get('phone'),
        role=data.get('role', 'user')
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': user.to_dict()
    })


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用户信息"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 只能修改自己的信息或管理员可以修改所有人
    if current_user.role != 'admin' and current_user_id != user_id:
        return jsonify({'code': 403, 'message': '无权限操作'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': user.to_dict()
    })


@app.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@jwt_required()
def reset_user_password(user_id):
    """管理员重置用户密码"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 只有管理员可以重置密码
    if current_user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限操作'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password:
        return jsonify({'code': 400, 'message': '新密码不能为空'}), 400
    
    # 设置新密码
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '密码重置成功'
    })


# ==================== 大拇哥管理 API ====================

@app.route('/api/thumbs', methods=['POST'])
@jwt_required()
def give_thumbs():
    """发放大拇哥"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'code': 403, 'message': '只有管理员可以发放大拇哥'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    thumb_type = data.get('thumb_type')  # 'single' or 'double'
    reason = data.get('reason', '')
    
    if not user_id or not thumb_type:
        return jsonify({'code': 400, 'message': '参数不完整'}), 400
    
    if thumb_type not in ['single', 'double']:
        return jsonify({'code': 400, 'message': '大拇哥类型错误'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    # 计算积分（单大拇哥=1分，双大拇哥=5分）
    points = 1 if thumb_type == 'single' else 5
    
    # 创建记录
    record = ThumbsRecord(
        user_id=user_id,
        thumb_type=thumb_type,
        points=points,
        reason=reason,
        given_by=current_user_id
    )
    
    # 更新用户积分
    user.total_points += points
    user.available_points += points
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': f'成功发放{"单" if thumb_type == "single" else "双"}大拇哥',
        'data': record.to_dict()
    })


@app.route('/api/thumbs', methods=['GET'])
@jwt_required()
def get_thumbs_records():
    """获取大拇哥记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    
    query = ThumbsRecord.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    pagination = query.order_by(ThumbsRecord.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'data': {
            'list': [record.to_dict() for record in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@app.route('/api/thumbs/stats', methods=['GET'])
@jwt_required()
def get_thumbs_stats():
    """获取大拇哥统计"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        current_user_id = get_jwt_identity()
        user_id = current_user_id
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    # 统计单双大拇哥数量
    single_count = ThumbsRecord.query.filter_by(user_id=user_id, thumb_type='single').count()
    double_count = ThumbsRecord.query.filter_by(user_id=user_id, thumb_type='double').count()
    
    return jsonify({
        'code': 200,
        'data': {
            'user_id': user_id,
            'user_name': user.real_name,
            'total_points': user.total_points,
            'available_points': user.available_points,
            'used_points': user.total_points - user.available_points,
            'single_thumbs': single_count,
            'double_thumbs': double_count,
            'total_thumbs': single_count + double_count
        }
    })


# ==================== 商品管理 API ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """获取商品列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')  # 'on_shelf' or 'off_shelf'
    keyword = request.args.get('keyword', '')
    
    query = Product.query
    
    # 如果指定了状态则过滤
    if status:
        query = query.filter_by(status=status)
    
    # 关键词搜索
    if keyword:
        query = query.filter(Product.name.like(f'%{keyword}%'))
    
    pagination = query.order_by(Product.sort_order.asc(), Product.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'data': {
            'list': [product.to_dict() for product in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """获取商品详情"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    return jsonify({
        'code': 200,
        'data': product.to_dict()
    })


@app.route('/api/products', methods=['POST'])
@jwt_required()
def create_product():
    """创建商品"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限操作'}), 403
    
    data = request.get_json()
    name = data.get('name')
    points_required = data.get('points_required')
    
    if not name or not points_required:
        return jsonify({'code': 400, 'message': '商品名称和积分不能为空'}), 400
    
    product = Product(
        name=name,
        description=data.get('description'),
        image_url=data.get('image_url'),
        points_required=points_required,
        stock=data.get('stock', 0),
        status=data.get('status', 'off_shelf'),
        sort_order=data.get('sort_order', 0)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': product.to_dict()
    })


@app.route('/api/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """更新商品信息"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限操作'}), 403
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'points_required' in data:
        product.points_required = data['points_required']
    if 'stock' in data:
        product.stock = data['stock']
    if 'status' in data:
        product.status = data['status']
    if 'sort_order' in data:
        product.sort_order = data['sort_order']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': product.to_dict()
    })


@app.route('/api/products/<int:product_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_product_status(product_id):
    """切换商品上下架状态"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限操作'}), 403
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    # 切换状态
    product.status = 'off_shelf' if product.status == 'on_shelf' else 'on_shelf'
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': f'商品已{"上架" if product.status == "on_shelf" else "下架"}',
        'data': product.to_dict()
    })


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """删除商品"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限操作'}), 403
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    # 检查是否有兑换记录
    if ExchangeRecord.query.filter_by(product_id=product_id).first():
        return jsonify({'code': 400, 'message': '该商品有兑换记录，不能删除'}), 400
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


# ==================== 兑换管理 API ====================

@app.route('/api/exchanges', methods=['POST'])
@jwt_required()
def create_exchange():
    """创建兑换记录"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'code': 400, 'message': '商品ID不能为空'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    if product.status != 'on_shelf':
        return jsonify({'code': 400, 'message': '商品已下架，无法兑换'}), 400
    
    if product.stock < quantity:
        return jsonify({'code': 400, 'message': '商品库存不足'}), 400
    
    points_needed = product.points_required * quantity
    if user.available_points < points_needed:
        return jsonify({'code': 400, 'message': '积分不足'}), 400
    
    # 创建兑换记录
    record = ExchangeRecord(
        user_id=current_user_id,
        product_id=product_id,
        product_name=product.name,
        points_spent=points_needed,
        quantity=quantity,
        status='completed'
    )
    
    # 扣除积分和库存
    user.available_points -= points_needed
    product.stock -= quantity
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '兑换成功',
        'data': record.to_dict()
    })


@app.route('/api/exchanges', methods=['GET'])
@jwt_required()
def get_exchanges():
    """获取兑换记录"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    status = request.args.get('status')
    
    query = ExchangeRecord.query
    
    # 普通用户只能查看自己的记录
    if current_user.role != 'admin':
        query = query.filter_by(user_id=current_user_id)
    elif user_id:
        query = query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(ExchangeRecord.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'data': {
            'list': [record.to_dict() for record in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@app.route('/api/exchanges/<int:record_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_exchange(record_id):
    """取消兑换（退回积分和库存）"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    record = ExchangeRecord.query.get(record_id)
    if not record:
        return jsonify({'code': 404, 'message': '兑换记录不存在'}), 404
    
    # 只有管理员或本人可以取消
    if current_user.role != 'admin' and record.user_id != current_user_id:
        return jsonify({'code': 403, 'message': '无权限操作'}), 403
    
    if record.status != 'completed':
        return jsonify({'code': 400, 'message': '只能取消已完成的兑换'}), 400
    
    # 退回积分
    user = User.query.get(record.user_id)
    user.available_points += record.points_spent
    
    # 退回库存
    product = Product.query.get(record.product_id)
    if product:
        product.stock += record.quantity
    
    record.status = 'cancelled'
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '兑换已取消，积分已退回',
        'data': record.to_dict()
    })


# ==================== 统计 API ====================

@app.route('/api/stats/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """获取仪表板统计数据"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role == 'admin':
        # 管理员看全局统计
        total_users = User.query.filter_by(role='user').count()
        total_thumbs = ThumbsRecord.query.count()
        total_exchanges = ExchangeRecord.query.filter_by(status='completed').count()
        total_products = Product.query.filter_by(status='on_shelf').count()
        
        return jsonify({
            'code': 200,
            'data': {
                'total_users': total_users,
                'total_thumbs': total_thumbs,
                'total_exchanges': total_exchanges,
                'total_products': total_products
            }
        })
    else:
        # 普通用户看个人统计
        return jsonify({
            'code': 200,
            'data': {
                'total_points': current_user.total_points,
                'available_points': current_user.available_points,
                'used_points': current_user.total_points - current_user.available_points,
                'total_thumbs': ThumbsRecord.query.filter_by(user_id=current_user_id).count(),
                'total_exchanges': ExchangeRecord.query.filter_by(user_id=current_user_id, status='completed').count()
            }
        })


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'code': 404, 'message': '资源不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


# ==================== 主程序 ====================

if __name__ == '__main__':
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否存在管理员，如果不存在则创建
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                real_name='系统管理员',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('已创建默认管理员账号: admin / admin123')
    
    app.run(host='0.0.0.0', port=5000, debug=True)

