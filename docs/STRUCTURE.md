# 项目结构说明（重构版）

## 📁 目录结构

```
word/
├── src/                              # 源代码
│   ├── config.example.py             # 配置模板
│   ├── config.py                     # 配置入口（支持 .env）
│   ├── main.py                       # 主程序入口
│   │
│   ├── core/                         # 核心功能模块
│   │   ├── database.py               # 向后兼容层
│   │   ├── db/                       # Repository 结构
│   │   │   ├── manager.py            # DatabaseManager 入口
│   │   │   ├── connection.py         # 连接/默认路径
│   │   │   ├── schema.py             # 表结构初始化
│   │   │   └── *_repository.py       # 业务仓储
│   │   ├── word_parser.py            # 词库解析（TXT/CSV/Excel）
│   │   ├── word_selector.py          # 艾宾浩斯选择器
│   │   ├── example_fetcher.py        # 例句/图片/音频获取
│   │   ├── email_sender.py           # 邮件发送
│   │   └── notifier.py               # 通知推送
│   │
│   ├── api/                          # Web API
│   │   ├── routes/                   # 页面路由
│   │   ├── rest_api.py               # Swagger/REST API
│   │   └── endpoints.py              # REST 端点
│   │
│   ├── services/                     # 业务服务层
│   │   ├── auth_service.py
│   │   ├── word_service.py
│   │   └── stats_service.py
│   │
│   ├── web/                          # Web管理服务
│   │   ├── app.py                    # Flask应用（App Factory）
│   │   └── templates/                # HTML模板
│   │       ├── layout.html           # 布局模板
│   │       ├── statistics.html       # 统计面板
│   │       ├── books.html            # 词书管理
│   │       ├── words.html            # 单词管理
│   │       ├── my_words.html         # 我的单词
│   │       ├── settings.html         # 系统设置
│   │       ├── login.html            # 登录
│   │       └── register.html         # 注册
│   │
│   └── data/                         # 数据文件
│       ├── CET4_edited.txt           # 默认词库（CET4）
│       ├── word.db                   # SQLite数据库（自动生成）
│       ├── word_history.json         # 旧版学习记录（兼容）
│       └── email_template.html       # 邮件模板
│
├── scripts/                          # 部署脚本
│   ├── deploy_docker.sh              # Docker一键部署
│   ├── docker_scheduler.py           # Docker定时调度器
│   ├── migrate_to_sqlite.py          # 数据迁移脚本
│   └── migrate_v2.py                 # V2版本迁移
│
├── docs/                             # 文档
│   ├── STRUCTURE.md                  # 本文件
│   ├── OPTIMIZATION_PLAN.md          # 优化计划
│   └── ROADMAP.md                    # 开发路线图
│
├── logs/                             # 日志目录
├── tests/                            # 测试用例
├── .env.example                      # 环境变量模板
├── docker-compose.yml                # Docker编排配置
├── Dockerfile                        # Docker镜像构建
└── README.md                         # 项目说明
```

## 🔑 核心模块说明

### src/main.py
主程序入口，负责：
- 初始化日志系统
- 读取配置（.env → src/config.py）
- 选择单词（新词+复习词）
- 获取例句、图片、音频
- 发送邮件
- 记录发送状态

### src/core/db/manager.py
数据库统一入口（Repository 模式），负责：
- 连接初始化与表结构创建
- 委托业务查询给各 Repository
- 向后兼容旧接口

### src/core/word_selector.py
艾宾浩斯记忆曲线实现：
- 掌握度与复习间隔（1/2/4/7/15/30天）
- 直接从 SQLite 读取/更新学习记录

### src/api/
REST API 与 Swagger 文档（`/api/v1/doc`）：
- 认证、单词、词书、统计等接口

### src/web/app.py
Flask Web 管理端：
- 页面路由 + REST API
- 登录/注册/登出
- `/health` 健康检查

## 📦 数据文件

### src/data/word.db
SQLite 数据库文件（自动生成）。包含：
- 词书与单词
- 用户与绑定
- 系统/用户设置
- 旧版学习记录兼容表

### src/data/word_history.json
旧版学习记录（兼容用，V2 已迁移到 SQLite）。

### src/data/email_template.html
邮件 HTML 模板。

## 🔧 配置方式

推荐使用 `.env`：

```bash
cp .env.example .env
```

`src/config.py` 会自动加载 `.env`。

## 📊 运行流程

1. **定时触发**（Cron 或 Docker Scheduler）
2. **单词选择**（新词 + 到期复习词）
3. **内容获取**（例句/图片/音频）
4. **邮件发送**
5. **记录更新**（数据库）

## 🌐 Web 服务

启动：

```bash
python3 -m flask --app src/web/app:app run
```

访问：http://localhost:5000

功能：
- 统计面板、词书管理、单词管理、我的单词、系统设置
- Swagger 文档：`/api/v1/doc`

## 📝 日志系统

日志文件：`logs/word_system.log`

## 🧪 测试

运行测试：

```bash
python3 -m pytest tests/
```

手动测试：

```bash
python3 src/main.py
```

## 📚 依赖说明

主要依赖：
- Flask - Web 框架
- Flask-RESTX - REST API / Swagger
- SQLite - 数据存储
- Requests - HTTP 客户端
- Pandas - 词书解析
- python-dotenv - 环境变量加载

## 🔄 更新日志

### v2.x（重构版）
- ✅ Repository 模式数据库结构
- ✅ 多用户登录/绑定
- ✅ REST API + Swagger
- ✅ 配置统一为 .env
- ✅ 修复部署脚本路径
- ✅ 完整测试通过
