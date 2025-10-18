-- 创建数据库
CREATE DATABASE IF NOT EXISTS thumbs_mall CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE thumbs_mall;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    role ENUM('admin', 'user') DEFAULT 'user',
    total_points INT DEFAULT 0 COMMENT '总积分',
    available_points INT DEFAULT 0 COMMENT '可用积分',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 大拇哥记录表
CREATE TABLE IF NOT EXISTS thumbs_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    thumb_type ENUM('single', 'double') NOT NULL COMMENT '单大拇哥或双大拇哥',
    points INT NOT NULL COMMENT '获得积分数',
    reason VARCHAR(255) COMMENT '获得原因',
    given_by INT COMMENT '发放人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (given_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='大拇哥记录表';

-- 商品表
CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    points_required INT NOT NULL COMMENT '所需积分',
    stock INT DEFAULT 0 COMMENT '库存数量',
    status ENUM('on_shelf', 'off_shelf') DEFAULT 'off_shelf' COMMENT '上架/下架状态',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_sort_order (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';

-- 兑换记录表
CREATE TABLE IF NOT EXISTS exchange_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    points_spent INT NOT NULL COMMENT '消耗积分',
    quantity INT DEFAULT 1 COMMENT '兑换数量',
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending' COMMENT '兑换状态',
    remark VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='兑换记录表';

-- 插入默认管理员账号 (密码: admin123)
INSERT INTO users (username, password, real_name, role, total_points, available_points) VALUES
('admin', 'pbkdf2:sha256:260000$salt$hash', '系统管理员', 'admin', 0, 0);

-- 插入测试用户 (密码: user123)
INSERT INTO users (username, password, real_name, email, total_points, available_points) VALUES
('zhangsan', 'pbkdf2:sha256:260000$salt$hash', '张三', 'zhangsan@example.com', 100, 100),
('lisi', 'pbkdf2:sha256:260000$salt$hash', '李四', 'lisi@example.com', 50, 50);

-- 插入测试商品
INSERT INTO products (name, description, points_required, stock, status, sort_order) VALUES
('小米充电宝', '10000mAh 快充移动电源', 50, 10, 'on_shelf', 1),
('星巴克咖啡券', '中杯任意饮品兑换券', 30, 20, 'on_shelf', 2),
('定制水杯', '公司logo定制保温杯', 80, 5, 'on_shelf', 3),
('京东卡100元', '京东购物卡100元面额', 100, 8, 'on_shelf', 4),
('无线鼠标', '罗技无线办公鼠标', 60, 0, 'off_shelf', 5);

-- 插入测试大拇哥记录
INSERT INTO thumbs_records (user_id, thumb_type, points, reason, given_by) VALUES
(2, 'double', 2, '项目按时交付，表现优秀', 1),
(2, 'single', 1, '积极参与团队活动', 1),
(3, 'single', 1, '帮助同事解决技术问题', 1);



