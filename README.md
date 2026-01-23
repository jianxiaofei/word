# 📚 单词邮件学习系统

> 基于艾宾浩斯记忆曲线的英语单词学习系统，每天通过精美的HTML邮件帮助你高效记忆单词

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Algorithm](https://img.shields.io/badge/Algorithm-Verified-success.svg)](tests/README.md)
[![Ebbinghaus](https://img.shields.io/badge/Ebbinghaus-1%2C2%2C4%2C7%2C15%2C30-orange.svg)](tests/VALIDATION_SUMMARY.md)

## ✨ 功能特性

- 📧 **智能邮件推送** - 每天早7:30自动发送（可配置时间）
- 🧠 **艾宾浩斯复习** - 科学的间隔重复算法（1/2/4/7/15/30天）
- 🎨 **精美HTML模板** - 渐变卡片设计，图文音频结合
- 🖼️ **图片记忆** - 自动获取单词相关图片（必应/Pixabay）
- 🔊 **音频发音** - 内嵌有道词典真人发音
- 📝 **双语例句** - 原文+翻译折叠显示，主动学习
- 📊 **Web管理面板** - 可视化学习进度和掌握度分布
- 🔐 **多用户登录/注册** - 支持管理员与普通用户
- 🧩 **REST API + Swagger** - `/api/v1/doc` 在线文档
- 🔄 **自动复习提醒** - 根据记忆曲线智能安排复习
- 📈 **掌握度分级** - L0-L5六级掌握度评估
- 📚 **多词书支持** - 支持上传自定义词书（TXT/CSV/Excel）
- ⚙️ **Web配置管理** - 可通过Web界面管理所有设置
- 🐳 **Docker部署** - 一键Docker Compose部署

## 📸 效果预览

### 邮件界面
- 渐变色卡片设计
- 单词 + 音标 + 内嵌音频播放器
- 配图辅助记忆
- 双语例句（可折叠）
- 学习进度条

### Web管理面板
- 📊 统计面板：已学单词数、复习次数、掌握率
- 📈 连续学习天数统计
- 🎨 掌握度分布彩色条形图
- 📉 最近30天学习趋势图
- 📚 词书管理：上传/切换词书
- 📝 单词管理：查看所有单词学习状态
- ⚙️ 系统设置：配置邮箱、每日单词数等

## 🚀 快速开始

### 前置要求

- Python 3.9+
- 邮箱账号（推荐QQ邮箱，需开启SMTP服务）
- 服务器（可选，用于定时发送）

### 1. 克隆项目

```bash
git clone https://github.com/jianxiaofei/word.git
cd word
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置邮箱（推荐使用 .env）

在项目根目录创建 `.env` 文件（可直接复制模板）：

```bash
cp .env.example .env
```

然后按需修改：

```dotenv
# SMTP 配置
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USE_TLS=true
EMAIL_FROM=your@qq.com
SMTP_PASSWORD=your_auth_code

# 收件人
EMAIL_TO=recipient@outlook.com

# 学习配置（可选）
DAILY_NEW_WORDS=5
SERVER_URL=

# Web 管理员账号（可选）
WEB_ADMIN_USER=admin
WEB_ADMIN_PASSWORD=your_strong_password
WEB_SECRET_KEY=your_long_random_string
WEB_ALLOW_REGISTER=true
```

配置项会自动从 `.env` 读取（见 `src/config.py`）。`src/config.example.py` 仍可作为参考模板。

> 💡 **获取QQ邮箱SMTP授权码**：登录QQ邮箱 → 设置 → 账户 → POP3/IMAP/SMTP服务 → 开启并获取授权码

### 4. 运行测试

```bash
# 测试邮件发送
python3 src/main.py

# 启动 Web 管理面板（访问 http://localhost:5000）
python3 -m flask --app src/web/app:app run
```

### 5. 部署到服务器（推荐 Docker）

#### Docker 部署

1. 确保已安装 Docker 和 Docker Compose
2. 配置 `.env`（参考步骤3）
3. 准备 Nginx 配置（如首次部署）：

```bash
mkdir -p nginx
cp docs/nginx.example.conf nginx/default.conf
```
4. 启动服务：

```bash
# 使用一键部署脚本（推荐）
./scripts/deploy_docker.sh

# 或者手动启动
docker-compose up -d
```

这将启动三个容器：
- `word-nginx`: 反向代理入口，访问 http://localhost/word-web/
- `word-web`: Web管理面板
- `word-scheduler`: 定时任务调度器，每天 07:30 自动发送邮件

#### 传统 Crontab 部署

```bash
# 每天7:30执行
30 7 * * * cd /root/word && python3 src/main.py
```

## 🌐 Web管理面板

启动后访问 `http://localhost:5000`（本地）或 `http://your-server/word-web/`（Docker）

REST API 文档：`/api/v1/doc`

### 登录保护（推荐开启）

Web 管理面板默认需要登录（会跳到 `/login`）。在服务器部署目录（默认 `/root/word`）创建/编辑 `.env`：

```dotenv
WEB_ADMIN_USER=admin
WEB_ADMIN_PASSWORD=your_strong_password
WEB_SECRET_KEY=your_long_random_string

# 可选：是否允许用户自行注册（默认 true）
WEB_ALLOW_REGISTER=true
```

修改后重启：`docker compose up -d --build`。

#### 普通用户注册/登录与单词绑定

- 访问 `/register` 可注册普通用户（若 `WEB_ALLOW_REGISTER=true`）。
- 普通用户登录后可以在“单词列表”里对单词进行“绑定/取消绑定”，并在“我的单词”查看已绑定单词。
- 管理员仍通过 `WEB_ADMIN_USER/WEB_ADMIN_PASSWORD` 登录，建议用于词书管理与系统设置。

### 页面功能

| 页面 | 路径 | 功能说明 |
|------|------|---------|
| 📊 统计面板 | `/` | 学习进度、掌握度分布、趋势图（Docker 部署时外部访问为 `/word-web/`） |
| 📚 词书管理 | `/books` | 上传/切换/管理词书 |
| 📝 单词管理 | `/words` | 查看所有单词学习状态 |
| 🧾 我的单词 | `/words/my` | 登录用户的单词与筛选 |
| ⚙️ 系统设置 | `/settings` | 配置邮箱、每日单词数等 |
| ❤️ 健康检查 | `/health` | 健康检查接口 |

## 📁 项目结构
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
├── tests/                            # 测试用例
├── logs/                             # 日志目录
├── docs/                             # 文档
│   ├── STRUCTURE.md                  # 项目结构详解
│   ├── OPTIMIZATION_PLAN.md          # 优化计划
│   └── ROADMAP.md                    # 开发路线图
│
├── docker-compose.yml                # Docker编排配置
├── Dockerfile                        # Docker镜像构建
├── nginx/                            # Nginx 配置（首次部署需创建）
│   └── default.conf                  # 从 docs/nginx.example.conf 复制
├── requirements.txt                  # Python依赖
└── README.md                         # 项目说明（本文件）
```

## 💾 SQLite 稳定性与备份（推荐）

项目默认使用 SQLite。已启用 WAL 以提升并发稳定性。

### 备份（建议每天一次）

服务器上可以用脚本做一致性备份（兼容 WAL）：

```bash
cd /root/word
python3 scripts/backup_db.py
```

可用 crontab 定时备份（示例：每天 03:10，保留 30 天）：

```bash
crontab -e
```

加入：

```cron
10 3 * * * cd /root/word && /usr/bin/python3 scripts/backup_db.py --keep-days 30 >> logs/backup.log 2>&1
```

## 🧠 艾宾浩斯记忆曲线

系统采用经典的艾宾浩斯记忆曲线进行复习安排：

| 掌握级别 | 复习间隔 | 说明 |
|---------|---------|------|
| L0 | 新学（当天） | 首次学习 |
| L1 | 1天后 | 第1次复习 |
| L2 | 2天后 | 第2次复习 |
| L3 | 4天后 | 第3次复习 |
| L4 | 7天后 | 第4次复习 |
| L5 | 15天后 | 第5次复习 |
| L6 | 30天后 | 完全掌握 |

**每日邮件组成**：N个新词 + M个到期复习词（可在设置中配置）

### 🔬 算法验证

✅ **已通过完整验证** (2026-01-23)

核心算法经过严格测试和验证，确保实现正确：
- ✅ 复习间隔配置正确 `[1, 2, 4, 7, 15, 30]`
- ✅ 新单词学习流程准确
- ✅ 复习进度推进逻辑无误
- ✅ 记忆效果显著：30天后可保持 94% 记忆（vs 不复习仅剩 48%）

**查看完整验证报告**: [tests/README.md](tests/README.md)

**运行验证测试**:
```bash
# 完整验证测试
python3 tests/test_ebbinghaus.py

# 可视化展示
python3 tests/visualize_ascii.py
```

**验证文档**:
- 📄 [验证总结](tests/VALIDATION_SUMMARY.md) - 最全面的验证报告
- 📊 [详细报告](tests/ebbinghaus_report.md) - 可视化验证过程
- 🧪 [测试脚本](tests/test_ebbinghaus.py) - 自动化验证工具
- 🎨 [可视化工具](tests/visualize_ascii.py) - 文本可视化展示

### 🎯 混合反馈机制

**v2.0 新特性** - 平衡用户体验与系统稳定性

系统采用**混合方案**，结合用户主动反馈和自动容错：

1. **发送邮件时**：
   - 新单词：立即标记为学习中
   - 复习单词：记录发送日期，等待反馈

2. **用户反馈（24小时内）**：
   - 点击"✓ 认识"：正常推进复习进度
   - 点击"✗ 不认识"：重置为L0重新学习
   - 邮件中有明确的反馈按钮

3. **24小时后未反馈**：
   - 系统自动按"认识"处理
   - 更新复习日期，避免单词累积
   - 下次运行时自动执行

**优势**：
- ✓ 鼓励用户主动回忆（艾宾浩斯核心）
- ✓ 避免单词无限累积
- ✓ 用户有缓冲时间，无焦虑
- ✓ 系统自动容错，保持稳定

详细说明：[tests/HYBRID_APPROACH.md](tests/HYBRID_APPROACH.md)

## 💾 数据存储

系统使用 SQLite 数据库存储所有数据，数据文件位于 `src/data/word.db`。

### 数据库表结构

| 表名 | 说明 |
|------|------|
| `books` | 词书管理 |
| `words` | 单词数据及学习记录 |
| `users` | 用户信息 |
| `user_word_bindings` | 用户单词绑定 |
| `settings` | 系统/用户设置（前缀式存储） |
| `learning_records` | 旧版学习记录（兼容） |

### 单词记录字段

```json
{
  "id": 1,
  "book_id": 1,
  "word": "abandon",
  "phonetic": "/əˈbændən/",
  "definition": "v. 放弃，遗弃",
  "status": 1,
  "first_learned": "2025-11-14",
  "last_review": "2025-11-16",
  "next_review": "2025-11-20",
  "review_count": 2,
  "mastery_level": 2
}
```

## 🔌 REST API

Web 服务提供 REST API（Swagger 文档位于 `/api/v1/doc`）：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录 |
| POST | `/api/v1/auth/register` | 注册 |
| POST | `/api/v1/auth/logout` | 登出 |
| GET | `/api/v1/auth/me` | 当前用户 |
| GET | `/api/v1/words` | 单词列表（支持 `book_id`/`status`） |
| GET | `/api/v1/words/<id>` | 单词详情 |
| POST | `/api/v1/words/<id>/mark` | 标记单词（`action=known/unknown/skip`） |
| GET | `/api/v1/books` | 词库列表 |
| GET | `/api/v1/books/<id>` | 词库详情 |
| GET | `/api/v1/stats/user` | 用户统计 |
| GET | `/api/v1/stats/progress` | 学习进度（`days`） |
| GET | `/api/v1/stats/distribution` | 单词分布 |

### 示例：登录后获取统计数据
```bash
# 登录（会写入 session cookie）
curl -i -c cookies.txt -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# 获取统计数据
curl -b cookies.txt http://localhost:5000/api/v1/stats/user
```

## 🛠️ 技术栈

- **Python 3.9+** - 主语言
- **Flask** - Web框架
- **Flask-RESTX** - REST API / Swagger
- **SQLite** - 数据库存储
- **Jinja2** - 模板引擎
- **Requests** - HTTP客户端
- **Pandas** - 数据处理（词书解析）
- **python-dotenv** - 环境变量加载
- **Docker** - 容器化部署
- **SMTP** - 邮件发送协议

## 📝 配置说明

### SMTP配置

支持主流邮箱服务商：

| 邮箱 | SMTP服务器 | 端口 | 说明 |
|-----|-----------|------|-----|
| QQ邮箱 | smtp.qq.com | 587 | 推荐，需获取授权码 |
| 163邮箱 | smtp.163.com | 587 | 需开启SMTP服务 |
| Gmail | smtp.gmail.com | 587 | 需开启两步验证 |
| Outlook | smtp.office365.com | 587 | 需应用专用密码 |

### Crontab配置示例

```bash
# 每天7:30执行
30 7 * * * cd /root/word && python3 src/main.py

# 每天8:00执行
0 8 * * * cd /root/word && python3 src/main.py

# 每天早晚各一次
30 7,19 * * * cd /root/word && python3 src/main.py
```

> 💡 **推荐使用 Docker 部署**：无需配置 Crontab，自动处理定时任务。

## 🐛 常见问题

### 1. 邮件发送失败

**问题**：SMTP认证失败

**解决**：
- 确认使用的是**SMTP授权码**，不是邮箱登录密码
- 检查邮箱是否开启了SMTP服务
- 确认SMTP服务器地址和端口正确

### 2. 图片加载失败

**问题**：邮件中图片不显示

**解决**：
- 系统会自动尝试多个图片源（必应→Pixabay→LoremFlickr）
- 检查网络连接
- 部分邮件客户端可能阻止外部图片

### 3. 音频无法播放

**问题**：点击播放按钮没反应

**解决**：
- 音频已内嵌为Base64格式，不依赖外部链接
- 部分邮件客户端（如某些Web邮箱）可能不支持audio标签
- 建议使用Outlook、Thunderbird等原生邮件客户端

### 4. 定时任务不执行

**问题**：Crontab配置后没有收到邮件

**解决**：
```bash
# 1. 检查cron服务状态
systemctl status cron

# 2. 查看cron日志
tail -f /var/log/syslog | grep CRON

# 3. 检查脚本路径是否正确
crontab -l

# 4. 手动测试脚本
cd /root/word && python3 src/main.py
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议

## 👨‍💻 作者

**jianxiaofei**
- Email: xiaofei.jian@outlook.com
- GitHub: [@jianxiaofei](https://github.com/jianxiaofei)

## 🙏 致谢

- 词库来源：CET4官方词汇表
- 例句来源：有道词典API
- 图片来源：必应图片搜索、Pixabay、LoremFlickr
- 音频来源：有道词典发音API

## 📊 项目统计

- 📚 默认词库：CET4词汇
- 🎯 复习间隔：6个级别（艾宾浩斯曲线）
- 📧 邮件模板：响应式HTML5设计
- 📈 统计维度：10+项学习数据
- 🐳 部署方式：Docker / 传统部署
- 💾 数据存储：SQLite数据库

---

⭐ 如果这个项目对你有帮助，欢迎Star支持！

💡 有任何问题或建议，欢迎提Issue讨论！
