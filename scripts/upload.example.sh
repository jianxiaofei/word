#!/bin/bash
# 上传脚本模板 - 复制为 upload.sh 并配置服务器IP

SERVER="YOUR_SERVER_IP"  # 替换为你的服务器IP
USER="root"
LOCAL_DIR="/Users/jxf/word"
REMOTE_DIR="/root/word"

echo "======================================"
echo "上传单词邮件系统到阿里云服务器"
echo "======================================"

echo "正在上传文件..."
scp -r $LOCAL_DIR/* $USER@$SERVER:$REMOTE_DIR/

echo ""
echo "上传完成！"
echo ""
echo "下一步："
echo "1. SSH登录服务器:"
echo "   ssh $USER@$SERVER"
echo ""
echo "2. 运行部署脚本:"
echo "   cd $REMOTE_DIR"
echo "   chmod +x deploy.sh"
echo "   ./deploy.sh"
echo ""
