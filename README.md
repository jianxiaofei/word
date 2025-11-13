# 单词邮件系统

自动发送CET4单词到指定邮箱的Python系统。

## 功能特性

- ✅ 每工作日早上8点自动发送5个随机单词
- ✅ 精美的HTML邮件卡片样式
- ✅ 自动记录已发送单词，确保不重复
- ✅ 学习进度追踪
- ✅ 使用本地Postfix邮件服务器发送
- ✅ 完整的日志记录

## 系统架构

```
word/
├── CET4_edited.txt          # CET4词库（4615个单词）
├── main.py                  # 主程序
├── config.py                # 配置文件
├── word_parser.py           # 词库解析模块
├── word_selector.py         # 单词选择模块
├── email_sender.py          # 邮件发送模块
├── email_template.html      # HTML邮件模板
├── requirements.txt         # Python依赖
├── deploy.sh                # 自动部署脚本
├── word_history.json        # 单词历史记录（自动生成）
├── word_system.log          # 系统日志（自动生成）
└── README.md                # 本文件
```

## 部署步骤

### 1. 配置文件准备

```bash
# 1. 复制配置模板
cp config.example.py config.py

# 2. 编辑配置文件，填入真实信息
nano config.py
```

需要配置：
- `SMTP_USERNAME`: 你的QQ邮箱
- `SMTP_PASSWORD`: QQ邮箱SMTP授权码（[获取方法](https://service.mail.qq.com/detail/0/75)）
- `EMAIL_TO`: 收件人邮箱

```bash
# 3. 复制部署脚本模板
cp upload.example.sh upload.sh
cp remote_deploy.example.sh remote_deploy.sh

# 4. 编辑脚本，填入服务器IP
nano upload.sh  # 修改 SERVER="YOUR_SERVER_IP"
nano remote_deploy.sh  # 修改 SERVER_IP="YOUR_SERVER_IP"
```

### 2. 上传到服务器

```bash
# 使用scp上传整个目录
scp -r /Users/jxf/word root@YOUR_SERVER_IP:/root/
```

### 3. 服务器部署

SSH登录服务器并运行部署脚本：

```bash
ssh root@YOUR_SERVER_IP
cd /root/word
chmod +x deploy.sh
./deploy.sh
```

部署脚本会自动：
- 检查并安装Python3
- 安装Python依赖（jinja2）
- 安装并配置Postfix邮件服务器
- 测试程序运行
- 配置crontab定时任务
- 设置文件权限

## 使用说明

### 手动运行测试

```bash
cd /root/word
python3 main.py
```

### 查看日志

```bash
# 实时查看系统日志
tail -f /root/word/word_system.log

# 查看cron日志
tail -f /root/word/cron.log
```

### 查看学习进度

```bash
cat /root/word/word_history.json
```

### 修改配置

编辑 `config.py` 文件：

```python
# 修改收件人
EMAIL_TO = "your-email@example.com"

# 修改每次发送数量
WORDS_PER_EMAIL = 10
```

### 修改发送时间

```bash
# 编辑定时任务
crontab -e

# 当前配置：每工作日（周一到周五）早上8点
# 0 8 * * 1-5 cd /root/word && /usr/bin/python3 main.py

# 改为每天早上8点：
# 0 8 * * * cd /root/word && /usr/bin/python3 main.py

# 改为每天早上8点和晚上8点：
# 0 8,20 * * * cd /root/word && /usr/bin/python3 main.py
```

## 邮件服务器配置

系统使用本地Postfix作为SMTP服务器。部署脚本会自动配置，如果遇到问题：

### 检查Postfix状态

```bash
systemctl status postfix
```

### 查看邮件队列

```bash
mailq
```

### 测试邮件发送

```bash
echo "Test email" | mail -s "Test" your_email@example.com
```

### Postfix配置优化

编辑 `/etc/postfix/main.cf`：

```conf
# 设置主机名
myhostname = yourdomain.com

# 设置域名
mydomain = yourdomain.com

# 设置发件人域
myorigin = $mydomain
```

重启服务：
```bash
systemctl restart postfix
```

## 故障排查

### 邮件未收到

1. **检查日志**
   ```bash
   tail -50 /root/word/word_system.log
   ```

2. **检查Postfix日志**
   ```bash
   tail -50 /var/log/maillog
   ```

3. **检查邮件队列**
   ```bash
   mailq
   ```

4. **检查垃圾邮件箱**
   邮件可能被标记为垃圾邮件

### 定时任务未执行

```bash
# 检查cron服务
systemctl status crond

# 查看cron日志
tail -f /root/word/cron.log

# 检查定时任务
crontab -l
```

### Python错误

```bash
# 重新安装依赖
pip3 install -r requirements.txt --force-reinstall
```

## 进阶配置

### 启用错误通知邮件

编辑 `main.py`，取消注释错误通知部分：

```python
# 发送错误通知邮件
try:
    sender = EmailSender(SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_TO)
    sender.send_error_notification(str(e))
except:
    pass
```

### 自定义邮件样式

编辑 `email_template.html` 修改邮件样式：
- 修改颜色主题
- 调整字体和布局
- 添加更多内容

### 重置学习进度

```bash
rm /root/word/word_history.json
```

下次运行时会重新开始。

## 技术栈

- **Python 3**: 主要编程语言
- **Jinja2**: HTML模板引擎
- **Postfix**: SMTP邮件服务器
- **Cron**: 定时任务调度

## 维护建议

1. **定期检查日志**（每周）
   ```bash
   tail -100 /root/word/word_system.log
   ```

2. **备份历史记录**（每月）
   ```bash
   cp /root/word/word_history.json /root/word/word_history_backup_$(date +%Y%m%d).json
   ```

3. **清理旧日志**（每季度）
   ```bash
   > /root/word/word_system.log
   > /root/word/cron.log
   ```

## 许可证

MIT License

## 作者

JXF - 单词学习系统

---

📧 如有问题，请查看日志文件或联系管理员。
