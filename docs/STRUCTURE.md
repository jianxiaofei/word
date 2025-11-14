# 项目结构说明

## 📁 目录结构

```
word/
├── src/                           # 源代码目录
│   ├── __init__.py                # 包初始化
│   ├── config.py                  # 配置文件（需自行创建）
│   ├── config.example.py          # 配置模板
│   ├── main.py                    # 主程序入口
│   │
│   ├── core/                      # 核心功能模块
│   │   ├── __init__.py
│   │   ├── word_parser.py         # 词库解析器
│   │   ├── word_selector.py       # 艾宾浩斯单词选择器
│   │   ├── example_fetcher.py     # 例句/图片/音频获取
│   │   └── email_sender.py        # 邮件发送器
│   │
│   ├── web/                       # Web统计服务
│   │   ├── __init__.py
│   │   ├── app.py                 # Flask应用
│   │   └── templates/
│   │       └── statistics.html    # 统计面板
│   │
│   └── data/                      # 数据文件
│       ├── __init__.py
│       ├── CET4_edited.txt        # 词库（4537个单词）
│       ├── word_history.json      # 学习记录
│       └── email_template.html    # 邮件模板
│
├── scripts/                       # 部署脚本
│   ├── deploy.sh                  # 一键部署
│   ├── upload.sh                  # 文件上传
│   └── remote_deploy.sh           # 远程部署
│
├── logs/                          # 日志目录
│   └── cron.log                   # 定时任务日志
│
├── tests/                         # 测试用例
├── docs/                          # 文档
│   └── STRUCTURE.md               # 本文件
│
├── requirements.txt               # Python依赖
├── setup.py                       # 包安装配置
├── README.md                      # 项目说明
└── .gitignore                     # Git忽略配置
```

## 🔑 核心模块说明

### src/main.py
主程序入口，负责：
- 初始化日志系统
- 加载配置文件
- 解析词库
- 选择单词（新词+复习词）
- 获取例句、图片、音频
- 发送邮件
- 更新学习记录

### src/core/word_parser.py
词库解析器，支持解析格式：
```
365 abandon v.放弃；遗弃，抛弃；放纵
```

### src/core/word_selector.py
艾宾浩斯记忆曲线实现：
- 6级掌握度（L0-L5）
- 复习间隔：1/2/4/7/15/30天
- 智能选择新词和复习词
- 自动更新学习进度

### src/core/example_fetcher.py
多媒体内容获取：
- 从有道词典获取例句
- 从Bing/Pixabay获取相关图片
- 下载音频并转Base64编码
- 自动重试和降级策略

### src/core/email_sender.py
HTML邮件发送：
- 支持TLS/SSL加密
- Jinja2模板渲染
- 多媒体内容嵌入
- 发送状态验证

### src/web/app.py
Flask统计面板：
- `/` - Web统计页面
- `/api/stats` - 统计数据API
- `/api/words` - 单词列表API
- 学习进度可视化

## 📦 数据文件

### src/data/CET4_edited.txt
CET4词库文件，包含4537个单词，格式：
```
序号 单词 词性.释义
```

### src/data/word_history.json
学习记录文件（自动生成），结构：
```json
{
  "words": {
    "365": {
      "word": "abandon",
      "first_learned": "2025-11-14",
      "review_count": 2,
      "next_review": "2025-11-20",
      "mastery_level": 2
    }
  },
  "used_indices": [365, 866],
  "last_update": "2025-11-14T07:30:00"
}
```

### src/data/email_template.html
邮件HTML模板，包含：
- 渐变色卡片设计
- 内嵌Base64图片
- HTML5 audio播放器
- 可折叠的翻译（details标签）
- 响应式布局

## 🚀 部署脚本

### scripts/deploy.sh
一键部署脚本，自动完成：
1. 检查Python环境
2. 安装依赖
3. 创建必要目录
4. 验证配置文件
5. 配置Cron定时任务

### scripts/upload.sh
文件上传脚本，通过SCP上传：
- 源代码
- 配置文件
- 数据文件

### scripts/remote_deploy.sh
远程部署脚本，SSH到服务器执行deploy.sh

## 🔧 配置文件

### src/config.py
主配置文件，包含：
- SMTP服务器设置
- 邮箱账号密码
- 发件人/收件人
- 每日单词数量
- API密钥（可选）

创建方式：
```bash
cp src/config.example.py src/config.py
# 编辑config.py填入实际配置
```

## 📊 运行流程

1. **定时触发**（Cron）
   ```
   30 7 * * 1-5 cd /root/word && python3 src/main.py
   ```

2. **单词选择**
   - 从词库中随机选择3个新词
   - 从历史记录中选择2个到期复习词

3. **内容获取**
   - 查询有道词典获取例句
   - 搜索Bing/Pixabay获取相关图片
   - 下载音频并转Base64

4. **邮件发送**
   - 渲染HTML模板
   - 嵌入图片和音频（Base64）
   - 通过SMTP发送

5. **记录更新**
   - 更新单词学习时间
   - 增加复习次数
   - 计算下次复习日期
   - 提升掌握度等级

## 🌐 Web服务

启动统计面板：
```bash
cd /Users/jxf/word
python3 src/web/app.py
```

访问：http://localhost:8080

功能：
- 学习统计（已学单词、复习次数、掌握率）
- 连续学习天数
- 掌握度分布图
- 30天学习趋势
- 最近学习单词列表

## 📝 日志系统

日志文件：`logs/cron.log`

日志级别：
- INFO：正常运行信息
- WARNING：警告信息
- ERROR：错误信息

示例：
```
2025-11-14 07:30:01 [INFO] 单词邮件系统启动
2025-11-14 07:30:02 [INFO] 已加载 4537 个单词
2025-11-14 07:30:03 [INFO] 选择了 3 个新词, 2 个复习词
2025-11-14 07:30:10 [INFO] ✓ 邮件发送成功
```

## 🧪 测试

运行测试（待完善）：
```bash
python3 -m pytest tests/
```

手动测试：
```bash
# 测试词库解析
python3 -c "import sys; sys.path.insert(0, 'src'); from core.word_parser import WordParser; p = WordParser('src/data/CET4_edited.txt'); print(f'共 {len(p.parse())} 个单词')"

# 测试单词选择
python3 -c "import sys; sys.path.insert(0, 'src'); from core.word_selector import WordSelectorV2; s = WordSelectorV2('src/data/word_history.json'); print(s.select_words(3, 2))"

# 测试邮件发送（需配置）
python3 src/main.py
```

## 📚 依赖说明

主要依赖（requirements.txt）：
- Flask >= 2.0.0 - Web框架
- Jinja2 >= 3.0.0 - 模板引擎
- requests >= 2.28.0 - HTTP客户端

可选依赖：
- BeautifulSoup4 - HTML解析（图片搜索）
- Pillow - 图片处理

## 🔄 更新日志

### v1.0.0 (2025-11-14)
- ✅ 简化目录结构（移除word_email层级）
- ✅ 统一配置文件路径
- ✅ 更新所有导入路径
- ✅ 修复部署脚本路径
- ✅ 完整测试通过
