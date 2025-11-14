#!/bin/bash
# 自动部署脚本 - 在服务器上执行

set -e

echo "======================================"
echo "单词邮件系统部署脚本"
echo "======================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 项目目录
PROJECT_DIR="/root/word"

# 1. 检查Python环境
echo -e "${GREEN}[1/5] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3未安装，正在安装...${NC}"
    if [ -f /etc/redhat-release ]; then
        yum install -y python3 python3-pip
    else
        apt-get update && apt-get install -y python3 python3-pip
    fi
fi
python3 --version

# 2. 安装依赖
echo -e "${GREEN}[2/5] 安装Python依赖...${NC}"
cd $PROJECT_DIR
pip3 install -r requirements.txt

# 3. 创建必要目录
echo -e "${GREEN}[3/5] 创建必要目录...${NC}"
mkdir -p logs

# 4. 配置检查
echo -e "${GREEN}[4/5] 检查配置文件...${NC}"
if [ ! -f "src/config.py" ]; then
    echo -e "${YELLOW}警告：配置文件不存在，请创建 src/config.py${NC}"
    echo -e "${YELLOW}参考：src/config.example.py${NC}"
    exit 1
fi

# 5. 配置Cron定时任务
echo -e "${GREEN}[5/5] 配置Cron定时任务...${NC}"
CRON_CMD="30 7 * * 1-5 cd $PROJECT_DIR && python3 src/main.py >> logs/cron.log 2>&1"

# 检查是否已存在
if crontab -l 2>/dev/null | grep -q "src/word_email/main.py"; then
    echo -e "${YELLOW}Cron任务已存在，跳过...${NC}"
else
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo -e "${GREEN}✓ Cron任务添加成功${NC}"
fi

echo -e "${GREEN}查看当前Cron任务：${NC}"
crontab -l | grep "word"

echo ""
echo "======================================"
echo -e "${GREEN}部署完成！${NC}"
echo "======================================"
echo ""
echo "📋 下一步操作："
echo "  1. 手动测试：python3 src/word_email/main.py"
echo "  2. 查看日志：tail -f logs/word_system.log"
echo "  3. 查看Cron日志：tail -f logs/cron.log"
echo "  4. 启动统计服务（可选）："
echo "     nohup python3 src/word_email/web/app.py > logs/web.log 2>&1 &"
echo ""
