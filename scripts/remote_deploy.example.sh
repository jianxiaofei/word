#!/bin/bash
# 远程部署脚本模板 - 复制为 remote_deploy.sh 并配置服务器IP

set -e

SERVER_IP="YOUR_SERVER_IP"  # 替换为你的服务器IP
SERVER_USER="root"
REMOTE_DIR="/root/word"
LOCAL_DIR="/Users/jxf/word"

echo "======================================"
echo "单词邮件系统 - 远程部署"
echo "======================================"

echo "[1/2] 上传文件到服务器..."
scp -r $LOCAL_DIR/* $SERVER_USER@$SERVER_IP:$REMOTE_DIR/

echo ""
echo "[2/2] 在服务器上执行部署..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
cd /root/word

echo "检查Python环境..."
python3 --version || yum install -y python3 python3-pip

echo "安装Python依赖..."
pip3 install -r requirements.txt

echo "检查并配置Postfix..."
if ! command -v postfix &> /dev/null; then
    yum install -y postfix
fi
systemctl enable postfix
systemctl start postfix

echo "配置定时任务..."
chmod +x /root/word/*.sh /root/word/main.py

# 移除旧的定时任务
crontab -l 2>/dev/null | grep -v "word.*main.py" | crontab - 2>/dev/null || true

# 添加新的定时任务（每工作日7:30）
(crontab -l 2>/dev/null; echo "30 7 * * 1-5 cd /root/word && /usr/bin/python3 main.py >> /root/word/cron.log 2>&1") | crontab -

echo ""
echo "测试运行..."
python3 /root/word/main.py

echo ""
echo "当前定时任务:"
crontab -l

echo ""
echo "✓ 部署完成！"
EOF

echo ""
echo "======================================"
echo "✓ 远程部署成功！"
echo "======================================"
