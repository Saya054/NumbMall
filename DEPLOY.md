# 大拇哥积分商城 - 部署指南

## 环境要求

### 后端
- Python 3.8+
- MySQL 8.0+

### 前端
- Node.js 16+
- npm 或 yarn

---

## 一、数据库部署

### 1. 安装 MySQL

Windows 系统可以从 [MySQL 官网](https://dev.mysql.com/downloads/mysql/) 下载安装包。

### 2. 创建数据库

```bash
# 登录 MySQL
mysql -u root -p

# 执行初始化脚本
source database/init.sql
```

或者直接导入：

```bash
mysql -u root -p < database/init.sql
```

### 3. 验证数据库

```sql
USE thumbs_mall;
SHOW TABLES;
```

应该看到以下表：
- users (用户表)
- thumbs_records (大拇哥记录表)
- products (商品表)
- exchange_records (兑换记录表)

---

## 二、后端部署

### 1. 进入后端目录

```bash
cd backend
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

如果下载速度慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 配置环境变量

复制 `.env.example` 并重命名为 `.env`（如果被忽略了，手动创建）：

```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=thumbs_mall

# Flask 配置
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production
```

**重要**: 修改 `MYSQL_PASSWORD` 为你的 MySQL 密码！

### 5. 启动后端服务

```bash
python app.py
```

后端服务将运行在 `http://localhost:5000`

成功启动后会看到：

```
 * Running on http://0.0.0.0:5000
已创建默认管理员账号: admin / admin123
```

---

## 三、前端部署

### 1. 进入前端目录

```bash
cd frontend
```

### 2. 安装依赖

```bash
npm install
```

如果安装速度慢，可以使用国内镜像：

```bash
npm install --registry=https://registry.npmmirror.com
```

或者使用 yarn：

```bash
yarn install
```

### 3. 启动开发服务器

```bash
npm run dev
```

前端服务将运行在 `http://localhost:5173`

### 4. 访问系统

打开浏览器访问: `http://localhost:5173`

---

## 四、默认账号

系统已经预置了以下测试账号：

### 管理员账号
- 用户名: `admin`
- 密码: `admin123`
- 权限: 可以管理用户、发放大拇哥、管理商品、管理兑换

### 普通用户账号
- 用户名: `zhangsan`
- 密码: `user123`
- 积分: 100

- 用户名: `lisi`
- 密码: `user123`
- 积分: 50

---

## 五、生产环境部署

### 后端部署（生产环境）

1. **使用 Gunicorn 运行**

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **配置 Nginx 反向代理**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

3. **配置系统服务（可选）**

创建 `/etc/systemd/system/thumbs-mall.service`:

```ini
[Unit]
Description=Thumbs Mall Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
systemctl start thumbs-mall
systemctl enable thumbs-mall
```

### 前端部署（生产环境）

1. **构建生产版本**

```bash
cd frontend
npm run build
```

2. **部署 dist 目录**

将生成的 `dist` 目录部署到 Web 服务器（如 Nginx）。

---

## 六、常见问题

### 1. 后端无法连接数据库

**错误**: `Can't connect to MySQL server`

**解决方案**:
- 检查 MySQL 服务是否启动
- 检查 `.env` 文件中的数据库配置是否正确
- 确认数据库用户有足够的权限

### 2. 前端无法访问后端 API

**错误**: `Network Error` 或 CORS 错误

**解决方案**:
- 确认后端服务已启动
- 检查 `vite.config.js` 中的代理配置
- 后端已经配置了 CORS，如果还有问题，检查防火墙设置

### 3. 登录后提示 Token 过期

**解决方案**:
- 检查系统时间是否正确
- 清除浏览器缓存和 localStorage
- 确认 `.env` 中的 `JWT_SECRET_KEY` 配置正确

### 4. npm install 失败

**解决方案**:
- 使用国内镜像源
- 清除 npm 缓存: `npm cache clean --force`
- 删除 `node_modules` 和 `package-lock.json` 后重新安装

### 5. 密码验证失败

**原因**: 数据库初始化脚本中的密码 hash 是占位符

**解决方案**: 
使用后端应用自动创建的管理员账号，或通过后端 API 创建新用户。

---

## 七、内网部署建议

对于内网环境：

1. **修改监听地址**
   - 后端: `app.run(host='0.0.0.0', port=5000)`
   - 前端: 修改 `vite.config.js` 的 server 配置

2. **配置防火墙**
   - 开放后端端口 5000
   - 开放前端端口 5173（开发）或 80/443（生产）

3. **使用局域网 IP**
   - 前端代理配置改为后端服务器的内网 IP
   - 或者统一通过 Nginx 代理

---

## 八、维护建议

### 数据备份

定期备份数据库：

```bash
mysqldump -u root -p thumbs_mall > backup_$(date +%Y%m%d).sql
```

### 日志管理

- 后端日志: 使用 Python logging 模块
- 前端错误: 使用浏览器开发者工具查看控制台

### 安全建议

1. 修改默认管理员密码
2. 使用强密码策略
3. 定期更新依赖包
4. 生产环境关闭 DEBUG 模式
5. 配置 HTTPS（如果需要外网访问）

---

## 九、技术支持

如有问题，请检查：
1. 后端日志输出
2. 前端浏览器控制台
3. MySQL 错误日志
4. 网络连接状态

系统架构简单清晰，适合内网快速部署和使用。



