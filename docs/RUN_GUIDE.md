# 🚀 启动指南

## 开发环境

### 方式 1：使用启动脚本（推荐）⭐
```bash
# 开发服务器（自动重载、调试模式）
python3 run_dev.py

# 或者直接运行
./run_dev.py
```

### 方式 2：Flask CLI
```bash
export FLASK_APP=src/web/app.py
export FLASK_DEBUG=1
flask run
```

### 方式 3：直接运行
```bash
python3 src/web/app.py
```

## 生产环境

### 方式 1：使用 Gunicorn 脚本
```bash
# 安装 gunicorn（如果还没安装）
pip install -r requirements.txt

# 启动生产服务器
python3 run_prod.py
```

### 方式 2：Docker 部署（推荐）⭐
```bash
docker-compose up -d
```

### 方式 3：手动启动 Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "src.web.app:app"
```

## 关于开发服务器警告

```
WARNING: This is a development server. Do not use it in a production deployment.
```

**这是正常的！**

- ✅ **开发/本地测试**：完全可以用，这就是它的设计目的
- ❌ **生产环境**：必须使用 Gunicorn/uWSGI 等 WSGI 服务器

## 端口说明

- **开发**: http://localhost:5000
- **生产 Docker**: http://your-server-ip/word-web/ (通过 Nginx 反向代理)

## 日志位置

- 开发环境：控制台输出
- 生产环境：`logs/access.log` 和 `logs/error.log`
