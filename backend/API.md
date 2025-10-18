# API 接口文档

## 基础信息

- 基础URL: `http://localhost:5000/api`
- 所有需要认证的接口都需要在请求头中携带 Token: `Authorization: Bearer <token>`

## 响应格式

```json
{
  "code": 200,
  "message": "成功",
  "data": {}
}
```

---

## 1. 认证相关

### 1.1 用户登录

**接口**: `POST /auth/login`

**请求参数**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "admin",
      "real_name": "系统管理员",
      "role": "admin"
    }
  }
}
```

### 1.2 获取当前用户信息

**接口**: `GET /auth/info`

**需要认证**: 是

---

## 2. 用户管理

### 2.1 获取用户列表

**接口**: `GET /users`

**需要认证**: 是

**查询参数**:
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 20)
- `keyword`: 搜索关键词

### 2.2 创建用户

**接口**: `POST /users`

**需要认证**: 是 (仅管理员)

**请求参数**:
```json
{
  "username": "zhangsan",
  "password": "123456",
  "real_name": "张三",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "role": "user"
}
```

### 2.3 更新用户信息

**接口**: `PUT /users/{user_id}`

**需要认证**: 是

---

## 3. 大拇哥管理

### 3.1 发放大拇哥

**接口**: `POST /thumbs`

**需要认证**: 是 (仅管理员)

**请求参数**:
```json
{
  "user_id": 2,
  "thumb_type": "single",
  "reason": "积极参与团队活动"
}
```

- `thumb_type`: "single" (单大拇哥👍, 1分) 或 "double" (双大拇哥👍👍, 5分)

### 3.2 获取大拇哥记录

**接口**: `GET /thumbs`

**需要认证**: 是

**查询参数**:
- `page`: 页码
- `per_page`: 每页数量
- `user_id`: 用户ID (可选)

### 3.3 获取大拇哥统计

**接口**: `GET /thumbs/stats`

**需要认证**: 是

**查询参数**:
- `user_id`: 用户ID (可选，默认当前用户)

**响应**:
```json
{
  "code": 200,
  "data": {
    "user_id": 2,
    "user_name": "张三",
    "total_points": 100,
    "available_points": 80,
    "used_points": 20,
    "single_thumbs": 50,
    "double_thumbs": 25,
    "total_thumbs": 75
  }
}
```

---

## 4. 商品管理

### 4.1 获取商品列表

**接口**: `GET /products`

**需要认证**: 否

**查询参数**:
- `page`: 页码
- `per_page`: 每页数量
- `status`: 商品状态 ("on_shelf" 或 "off_shelf")
- `keyword`: 搜索关键词

### 4.2 获取商品详情

**接口**: `GET /products/{product_id}`

**需要认证**: 否

### 4.3 创建商品

**接口**: `POST /products`

**需要认证**: 是 (仅管理员)

**请求参数**:
```json
{
  "name": "小米充电宝",
  "description": "10000mAh 快充移动电源",
  "image_url": "http://example.com/image.jpg",
  "points_required": 50,
  "stock": 10,
  "status": "on_shelf",
  "sort_order": 1
}
```

### 4.4 更新商品信息

**接口**: `PUT /products/{product_id}`

**需要认证**: 是 (仅管理员)

### 4.5 切换商品上下架状态

**接口**: `POST /products/{product_id}/toggle-status`

**需要认证**: 是 (仅管理员)

### 4.6 删除商品

**接口**: `DELETE /products/{product_id}`

**需要认证**: 是 (仅管理员)

---

## 5. 兑换管理

### 5.1 创建兑换记录

**接口**: `POST /exchanges`

**需要认证**: 是

**请求参数**:
```json
{
  "product_id": 1,
  "quantity": 1
}
```

### 5.2 获取兑换记录

**接口**: `GET /exchanges`

**需要认证**: 是

**查询参数**:
- `page`: 页码
- `per_page`: 每页数量
- `user_id`: 用户ID (管理员可用)
- `status`: 兑换状态

### 5.3 取消兑换

**接口**: `POST /exchanges/{record_id}/cancel`

**需要认证**: 是

---

## 6. 统计数据

### 6.1 获取仪表板统计

**接口**: `GET /stats/dashboard`

**需要认证**: 是

**响应 (管理员)**:
```json
{
  "code": 200,
  "data": {
    "total_users": 100,
    "total_thumbs": 500,
    "total_exchanges": 200,
    "total_products": 20
  }
}
```

**响应 (普通用户)**:
```json
{
  "code": 200,
  "data": {
    "total_points": 100,
    "available_points": 80,
    "used_points": 20,
    "total_thumbs": 50,
    "total_exchanges": 10
  }
}
```

