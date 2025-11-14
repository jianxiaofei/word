# 📚 单词邮件学习系统

> 基于艾宾浩斯记忆曲线的英语单词学习系统，每天通过精美的HTML邮件帮助你高效记忆单词

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 功能特性

- 📧 **智能邮件推送** - 每工作日早7:30自动发送（可配置）
- 🧠 **艾宾浩斯复习** - 科学的间隔重复算法（1/2/4/7/15/30天）
- 🎨 **精美HTML模板** - 渐变卡片设计，图文音频结合
- 🖼️ **图片记忆** - 自动获取单词相关图片（必应/Pixabay）
- 🔊 **音频发音** - 内嵌有道词典真人发音
- 📝 **双语例句** - 原文+翻译折叠显示，主动学习
- 📊 **Web统计面板** - 可视化学习进度和掌握度分布
- 🔄 **自动复习提醒** - 根据记忆曲线智能安排复习
- 📈 **掌握度分级** - L0-L5六级掌握度评估

## 📸 效果预览

### 邮件界面
- 渐变色卡片设计
- 单词 + 音标 + 内嵌音频播放器
- 配图辅助记忆
- 双语例句（可折叠）
- 学习进度条

### Web统计面板
- 已学单词数、复习次数、掌握率
- 连续学习天数统计
- 掌握度分布彩色条形图
- 最近30天学习趋势图
- 最近学习单词列表

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

### 3. 配置邮箱

复制配置文件模板：
```bash
cp src/config.example.py src/config.py
```

编辑 `src/config.py`，填入你的邮箱信息：

```python
# SMTP服务器配置
SMTP_SERVER = "smtp.qq.com"          # QQ邮箱SMTP服务器
SMTP_PORT = 587                      # TLS端口
SMTP_USE_TLS = True                  # 使用TLS加密
SMTP_USERNAME = "your@qq.com"        # 你的QQ邮箱
SMTP_PASSWORD = "your_auth_code"     # SMTP授权码（非密码！）

# 邮件配置
EMAIL_FROM = "your@qq.com"           # 发件人（同上）
EMAIL_TO = "recipient@outlook.com"   # 收件人邮箱

# 每封邮件单词数（新词+复习词）
WORDS_PER_EMAIL = 5                  # 3个新词 + 2个复习词
```

> 💡 **获取QQ邮箱SMTP授权码**：登录QQ邮箱 → 设置 → 账户 → POP3/IMAP/SMTP服务 → 开启并获取授权码

### 4. 运行测试

```bash
# 测试邮件发送
python3 src/main.py

# 启动统计服务（访问 http://localhost:8080）
python3 src/web/app.py
```

### 5. 部署到服务器（可选）

#### 方式1: 使用部署脚本

```bash
# 1. 复制部署脚本模板
cp scripts/upload.example.sh scripts/upload.sh
cp scripts/remote_deploy.example.sh scripts/remote_deploy.sh

# 2. 编辑脚本，填入服务器信息
nano scripts/upload.sh
nano scripts/remote_deploy.sh

# 3. 上传并部署
bash scripts/deploy.sh
```

#### 方式2: 手动部署

```bash
# 1. 上传文件到服务器
scp -r src/ requirements.txt root@your-server:/root/word/

# 2. SSH登录服务器
ssh root@your-server

# 3. 安装依赖
cd /root/word
pip3 install -r requirements.txt

# 4. 配置定时任务
crontab -e
# 添加以下行（每工作日7:30执行）
30 7 * * 1-5 cd /root/word && python3 src/main.py >> logs/cron.log 2>&1
```

## 📁 项目结构

```
word/
├── src/                              # 源代码
│   └── word_email/                   # 主包
│       ├── __init__.py               # 包初始化
│       ├── config.py                 # 配置文件（需自行创建）
│       ├── main.py                   # 主程序入口
│       │
│       ├── core/                     # 核心功能模块
│       │   ├── word_parser.py        # 词库解析
│       │   ├── word_selector.py      # 艾宾浩斯选择器
│       │   ├── example_fetcher.py    # 例句/图片/音频获取
│       │   └── email_sender.py       # 邮件发送
│       │
│       ├── web/                      # Web统计服务
│       │   ├── app.py                # Flask应用
│       │   └── templates/            # HTML模板
│       │       └── statistics.html   # 统计面板
│       │
│       └── data/                     # 数据文件
│           ├── CET4_edited.txt       # 词库（4537个单词）
│           ├── word_history.json     # 学习记录（自动生成）
│           └── email_template.html   # 邮件模板
│
├── scripts/                          # 部署脚本
│   ├── deploy.sh                     # 一键部署
│   ├── upload.sh                     # 文件上传
│   └── remote_deploy.sh              # 远程部署
│
├── tests/                            # 测试用例（待完善）
├── logs/                             # 日志目录
├── docs/                             # 文档
│   └── STRUCTURE.md                  # 项目结构详解
│
├── requirements.txt                  # Python依赖
├── setup.py                          # 安装配置
├── README.md                         # 项目说明（本文件）
└── .gitignore                        # Git忽略配置
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

**每日邮件组成**：3个新词 + 2个到期复习词

## 📊 数据结构

### word_history.json
```json
{
  "words": {
    "365": {
      "word": "abandon",
      "first_learned": "2025-11-14",
      "review_count": 2,
      "last_review": "2025-11-16",
      "next_review": "2025-11-20",
      "mastery_level": 2
    }
  },
  "used_indices": [365, 866, ...],
  "last_update": "2025-11-14T07:30:02.040000"
}
```

## 🔌 API接口

Web统计服务提供以下接口：

- `GET /` - Web统计面板（HTML页面）
- `GET /api/stats` - 统计数据（JSON格式）
- `GET /api/words` - 所有单词详情（JSON格式）

示例：
```bash
# 获取统计数据
curl http://localhost:8080/api/stats

# 返回示例
{
  "total_learned": 85,
  "total_reviews": 12,
  "mastery_rate": 15.3,
  "progress": 1.87,
  "streak_days": 5,
  "today_review_count": 2
}
```

## 🛠️ 技术栈

- **Python 3.9+** - 主语言
- **Flask** - Web框架
- **Jinja2** - 模板引擎
- **Requests** - HTTP客户端
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
# 每工作日7:30执行
30 7 * * 1-5 cd /root/word && python3 src/main.py

# 每天8:00执行
0 8 * * * cd /root/word && python3 src/main.py

# 每天早晚各一次
30 7,19 * * * cd /root/word && python3 src/main.py
```

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

- 📚 词库容量：4537个单词（CET4）
- 🎯 复习间隔：6个级别（艾宾浩斯曲线）
- 📧 邮件模板：响应式HTML5设计
- 📈 统计维度：10+项学习数据

---

⭐ 如果这个项目对你有帮助，欢迎Star支持！

💡 有任何问题或建议，欢迎提Issue讨论！
