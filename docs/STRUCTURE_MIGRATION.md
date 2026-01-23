# 目录结构调整说明

## 📁 主要变更

### 1. 数据文件移动
- `src/data/CET4_edited.txt` → `resources/CET4_edited.txt`（静态资源）
- `src/data/email_template.html` → `src/web/templates/email_template.html`
- 数据库文件 `src/data/word.db` 保持不变（运行时数据）

> **命名标准**：`resources/` 是 Python 项目中存放静态资源文件的标准目录名，比 `data/` 更符合最佳实践。

### 2. 配置文件重组
```
旧结构:
src/config.py
src/config.example.py

新结构:
src/config/
├── __init__.py
├── config.py
└── config.example.py
```

### 3. 测试文档整理
- `tests/*.md` → `docs/tests/`（将测试相关文档移至 docs）

### 4. 新增标准文件
- ✅ `pyproject.toml` - 项目配置和依赖管理
- ✅ `.gitignore` - 已完善（添加 `__pycache__`、日志等）
- ✅ `.env.example` - 环境变量模板

## 🔧 已更新的文件

### 配置文件
- [x] `src/config/config.py` - 路径更新
- [x] `src/config/config.example.py` - 路径更新
- [x] `src/config/__init__.py` - 新建模块导出

### 核心代码
- [x] `src/core/notifications/channels/email.py` - 模板路径更新

### 部署脚本
- [x] `scripts/deploy_docker.sh` - 配置文件路径更新
- [x] `scripts/deploy_image.sh` - 挂载路径更新
- [x] `Dockerfile` - 添加 data 目录创建

### 清理
- [x] 删除所有 `__pycache__` 目录
- [x] 删除 `src/web/app.py.bak`
- [x] 删除 `.DS_Store` 文件

## ⚠️ 兼容性说明

### 代码导入
所有 `import config` 语句**无需修改**，因为：
- `src/config/__init__.py` 重新导出了所有配置项
- Python 会自动将 `config` 包识别为模块

### Docker 部署
- **本地开发**：无影响，docker-compose.yml 挂载整个 src 目录
- **生产部署**：脚本已更新，使用新路径 `volumes/config/config.py:/app/src/config/config.py`

## 🚀 迁移步骤（如果需要在其他环境）

### 本地开发环境
```bash
# 1. 拉取最新代码
git pull

# 2. 重新配置（如果配置文件丢失）
cp src/config/config.example.py src/config/config.py
# 编辑 src/config/config.py

# 3. 重新配置环境变量（可选）
cp .env.example .env
# 编辑 .env

# 4. 重启服务
docker-compose down
docker-compose up -d --build
```

### 生产服务器
```bash
# 使用更新后的部署脚本
./scripts/deploy_image.sh --server-ip YOUR_IP

# 或使用 Docker 模式
./scripts/deploy_docker.sh --server-ip YOUR_IP
```

## 📋 文件路径对照表

| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `src/config.py` | `src/config/config.py` | 实际配置文件 |
| `src/config.example.py` | `src/config/config.example.py` | 配置模板 |
| `src/data/CET4_edited.txt` | `resources/CET4_edited.txt` | 词库数据（静态资源） |
| `src/data/email_template.html` | `src/web/templates/email_template.html` | 邮件模板 |
| `tests/*.md` | `docs/tests/*.md` | 测试文档 |

## ✅ 验证检查清单

- [ ] 配置导入正常：`python -c "import config; print(config.SMTP_SERVER)"`
- [ ] 邮件模板加载：检查 `src/web/templates/email_template.html` 存在
- [ ] 词库文件访问：检查 `resources/CET4_edited.txt` 存在
- [ ] Docker 构建成功：`docker-compose build`
- [ ] 服务启动正常：`docker-compose up -d`
- [ ] Web 面板访问：http://localhost/word-web/

## 🎯 优化效果

1. **更标准的目录结构**：符合 Python 项目最佳实践
   - `resources/` 存放静态资源文件（词库等）
   - `src/data/` 存放运行时数据（数据库等）
2. **更清晰的模块划分**：配置独立为模块，便于扩展
3. **更好的版本控制**：.gitignore 规则完善，避免提交临时文件
4. **更完整的项目配置**：pyproject.toml 支持现代 Python 工具链

---
更新时间：2026年1月23日
