#!/bin/bash
# 部署脚本 - 在阿里云服务器上运行

set -e

echo "======================================"
echo "单词邮件系统部署脚本"
echo "======================================"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="/root/word"

echo -e "${GREEN}[1/6] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3未安装，正在安装...${NC}"
    yum install -y python3 python3-pip
fi
python3 --version

echo -e "${GREEN}[2/6] 安装Python依赖...${NC}"
cd $PROJECT_DIR
pip3 install -r requirements.txt

echo -e "${GREEN}[3/6] 检查并配置Postfix邮件服务器...${NC}"
if ! command -v postfix &> /dev/null; then
    echo "安装Postfix..."
    yum install -y postfix
fi

# 配置Postfix
systemctl enable postfix
systemctl start postfix
systemctl status postfix --no-pager

# 检查防火墙
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=smtp 2>/dev/null || true
    firewall-cmd --reload 2>/dev/null || true
fi

echo -e "${GREEN}[4/6] 测试程序运行...${NC}"
cd $PROJECT_DIR
python3 main.py || {
    echo -e "${RED}程序测试运行失败，请检查日志${NC}"
    exit 1
}

echo -e "${GREEN}[5/6] 配置定时任务...${NC}"

# 创建cron任务
CRON_CMD="0 8 * * 1-5 cd $PROJECT_DIR && /usr/bin/python3 main.py >> $PROJECT_DIR/cron.log 2>&1"

# 检查是否已存在
if crontab -l 2>/dev/null | grep -q "word.*main.py"; then
    echo "定时任务已存在，更新中..."
    crontab -l 2>/dev/null | grep -v "word.*main.py" | crontab -
fi

# 添加新任务
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "当前定时任务列表:"
crontab -l

echo -e "${GREEN}[6/6] 设置文件权限...${NC}"
chmod +x $PROJECT_DIR/main.py
chmod +x $PROJECT_DIR/deploy.sh

echo ""
echo -e "${GREEN}======================================"
echo "✓ 部署完成！"
echo "======================================${NC}"
echo ""
echo "配置信息："
echo "  - 项目目录: $PROJECT_DIR"
echo "  - 发送时间: 每工作日 08:00"
echo "  - 收件人: 配置文件中指定的邮箱"
echo "  - 日志文件: $PROJECT_DIR/word_system.log"
echo "  - Cron日志: $PROJECT_DIR/cron.log"
echo ""
echo "常用命令："
echo "  - 查看日志: tail -f $PROJECT_DIR/word_system.log"
echo "  - 手动运行: cd $PROJECT_DIR && python3 main.py"
echo "  - 查看定时任务: crontab -l"
echo "  - 编辑定时任务: crontab -e"
echo "  - 查看Postfix状态: systemctl status postfix"
echo "  - 查看邮件队列: mailq"
echo ""
