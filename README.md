# 大拇哥积分家庭奖励系统

本项目面向家长，为家长提供一个「大拇哥」奖励平台，让孩子通过完成任务、好行为或学习成果获取积分，再使用积分兑换实物或体验奖励。项目包含 Web 管理端与家庭端，可在家庭局域网或公网部署。

---

## ✨ 核心能力
- **多家庭支持**：家长注册家庭账号后，可为每位孩子创建个人档案与积分账户。
- **奖励发放**：家长可在手机或电脑端快速发放／扣减「大拇哥」积分，支持备注原因与查看流水。
- **积分看板**：孩子登陆后可查看当前积分、累计奖励、最近表现等情况，增添激励。
- **奖励商城**：家长配置奖励项目（如周末游玩、玩具、额外屏幕时间等），孩子可选择一次性兑换多件，只要积分足够。
- **兑换审批**：可选的家长确认流程，避免孩子误操作或库存不足。
- **上传与分享**：奖励项目支持图片展示，家长可上传商品或活动图片增强吸引力。

## 🧱 技术栈
- **前端**：Vue 3、Vite、Pinia、Vue Router、Element Plus 组件库。
- **后端**：Flask、SQLAlchemy、Flask-JWT-Extended、CORS。
- **数据库**：MySQL（默认使用 `thumbs_mall` 库，可自定义）。

## 📁 目录结构
```
.
├─backend/                # Flask 后端服务
│  ├─app.py               # 业务路由：积分发放、奖励配置、兑换记录等
│  ├─config.py            # 配置加载（支持 .env）
│  ├─models.py            # 用户、孩子、积分及兑换模型
│  ├─API.md               # REST API 参考文档
│  ├─requirements.txt     # Python 依赖
│  ├─run.bat              # Windows 快速启动脚本（自动安装依赖/激活 venv）
│  ├─reset_admin.py       # 家长管理员重置脚本
│  ├─reset_passwords_simple.py # 批量重置家庭账号密码
│  └─uploads/             # 奖励图片存储目录
├─frontend/               # Vue 前端界面（家长和孩子共用）
│  ├─src/                 # 页面、布局、状态、接口封装
│  ├─package.json         # 前端依赖
│  └─vite.config.js       # Vite 配置
├─database/
│  └─init.sql             # 初始化数据库结构与演示数据（示例家庭、奖励）
├─DEPLOY.md               # 部署与上线指引
└─README.md               # 项目说明（当前文件）
```

## 🚀 快速部署指南
以下流程以 Windows + CMD/PowerShell 为例；其他平台可按命令格式调整。

### 1. 准备数据库
1. 安装并启动 MySQL（>=8.0，或使用 MariaDB 兼容版本）。
2. 创建数据库（默认 `thumbs_mall`，可在 `.env` 修改）。
3. 执行 `database/init.sql` 导入表结构与示例数据（含演示家长/孩子账号）。

### 2. 配置后端服务
```bash
cd backend
python -m venv venv          # 推荐使用虚拟环境
venv\Scripts\activate        # 激活虚拟环境（Windows）
pip install -r requirements.txt
```

> **环境配置**：复制 `.env.bak` 到 `.env`，根据实际数据库、密钥、端口等信息调整。生产部署时务必替换默认密钥。

启动后端服务（任选其一）：
```bash
# 直接启动
python app.py

# 或使用脚本（自动处理依赖/环境）
run.bat
```
服务默认地址：`http://localhost:5000`。

### 3. 启动前端界面
```bash
cd frontend
npm install          # 首次安装依赖
npm run dev          # 开发模式（默认端口 5173）
```

访问 `http://localhost:5173` 打开前端界面。前端默认把 API 请求发送到 `http://localhost:5000/api`，如需修改可调整 `frontend/src/utils/api.js` 中的 `baseURL`。

### 4. 默认账号
- **家长管理员**与**孩子体验账号**见 `database/init.sql`；可在首次登录后修改密码。
- 提供 `backend/reset_admin.py` 和 `backend/reset_passwords_simple.py` 帮助找回忘记的账号信息。

## 👪 使用场景建议
- 家长可把日常家务、学习任务记录为积分奖励规则，定期发放「大拇哥」积分。
- 孩子可在积分商城里兑换家庭时间、兴趣课程、玩具、外出活动等。
- 可基于兑换记录与积分流水，和孩子一起复盘良好习惯的养成情况。

## 🔧 常用命令速查
| 操作 | 命令 |
| ---- | ---- |
| 激活虚拟环境 | `venv\Scripts\activate` |
| 安装后端依赖 | `pip install -r requirements.txt` |
| 启动后端服务 | `python app.py` 或 `run.bat` |
| 启动前端 | `npm run dev` |
| 前端打包 | `npm run build` |
| 查看 API | 打开 `backend/API.md` |

## 🧩 常见问题
- **窗口闪退或文字乱码**：先在终端执行 `chcp 65001`，再运行 `run.bat`；脚本已采用 ASCII 文本避免解析失败。
- **数据库连接失败**：确认 `.env` 中的数据库主机、端口、账号、密码，与实际部署一致。
- **无法登录**：使用初始化 SQL 中的账号密码，或运行重置脚本获取新密码。
- **依赖安装慢**：脚本默认使用清华镜像，可换为本地私有镜像或官方源。
- **跨域请求报错**：后端已启用 CORS，若部署在不同域名，可在 `app.py` 中补充允许的来源。

## 📚 参考资料
- `backend/API.md`：详细的 REST 接口说明。
- `DEPLOY.md`：线上部署、Nginx 反向代理、HTTPS 等方案。
- `database/init.sql`：数据库结构及演示数据说明。

---

欢迎在实际使用中结合家庭需求调整奖励规则、前端文案或配色，让大拇哥积分成为亲子互动与习惯培养的好帮手！
