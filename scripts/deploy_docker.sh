#!/bin/bash
# Docker 一键部署脚本

set -euo pipefail

usage() {
    cat << 'USAGE'
用法:
    ./scripts/deploy_docker.sh <ip>
    ./scripts/deploy_docker.sh --server-ip <ip> [--server-user <user>] [--remote-dir <dir>] [--sync-data]

参数:
  --server-ip     目标服务器 IP（必填）
  --server-user   SSH 用户（默认: root）
  --remote-dir    远程部署目录（默认: /root/word）
  --sync-data     同步数据文件（迁移用：会覆盖远程 word.db/word_history.json）

示例:
    ./scripts/deploy_docker.sh 203.0.113.10
    ./scripts/deploy_docker.sh --server-ip 203.0.113.10
    ./scripts/deploy_docker.sh --server-ip 203.0.113.10 --sync-data
USAGE
}

SERVER_IP=""
SERVER_USER="root"
REMOTE_DIR="/root/word"
SYNC_DATA=0

# 兼容最简用法：./scripts/deploy_docker.sh <ip>
if [[ $# -ge 1 && "${1:-}" != "" && "${1:-}" != -* ]]; then
    SERVER_IP="$1"
    shift 1
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --server-ip)
            SERVER_IP="${2:-}"; shift 2 ;;
        --server-user)
            SERVER_USER="${2:-}"; shift 2 ;;
        --remote-dir)
            REMOTE_DIR="${2:-}"; shift 2 ;;
        --sync-data)
            SYNC_DATA=1; shift 1 ;;
        -h|--help)
            usage; exit 0 ;;
        *)
            echo "未知参数: $1" >&2
            usage
            exit 2
            ;;
    esac
done

# 允许无参数交互式输入
if [[ -z "$SERVER_IP" ]]; then
    read -r -p "请输入目标服务器 IP: " SERVER_IP
fi

if [[ -z "$SERVER_IP" ]]; then
    echo "缺少必填参数: --server-ip" >&2
    usage
    exit 2
fi

# 获取脚本所在目录的上一级目录作为项目根目录
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

echo "======================================"
echo "单词邮件系统 - Docker 远程部署"
echo "======================================"
echo "目标服务器: $SERVER_USER@$SERVER_IP"
echo "本地目录: $PROJECT_ROOT"
echo "远程目录: $REMOTE_DIR"
echo "======================================"

# 1. 上传文件
echo "[1/3] 正在同步文件..."

echo "创建远程目录..."
ssh "$SERVER_USER@$SERVER_IP" "mkdir -p '$REMOTE_DIR' '$REMOTE_DIR/logs' '$REMOTE_DIR/src/data'"

# 检查是否有 rsync，推荐使用 rsync 以排除不必要文件
if command -v rsync &> /dev/null; then
    rsync -avz --progress \
        --exclude '.git' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.DS_Store' \
        --exclude 'venv' \
        --exclude '.env' \
        --exclude 'src/data/word.db' \
        --exclude 'src/data/*.db' \
        --exclude 'src/data/*.db-wal' \
        --exclude 'src/data/*.db-shm' \
        --exclude 'nginx/default.conf' \
        "$PROJECT_ROOT/" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

    if [[ "$SYNC_DATA" -eq 1 ]]; then
        echo ""
        echo "[数据同步] 正在同步 src/data/word.db（将覆盖远程同名文件）..."
        rsync -avz --progress \
            "$PROJECT_ROOT/src/data/word.db" \
            "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/src/data/"

        if [[ -f "$PROJECT_ROOT/src/data/word_history.json" ]]; then
            echo "[数据同步] 同步 src/data/word_history.json（可选）..."
            rsync -avz --progress \
                "$PROJECT_ROOT/src/data/word_history.json" \
                "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/src/data/"
        fi
    fi
else
    echo "未找到 rsync，使用 scp (可能会上传多余文件)..."
    # scp 比较笨，这里简单处理，可能会覆盖
    scp -r "$PROJECT_ROOT/"* "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

    if [[ "$SYNC_DATA" -eq 1 ]]; then
        echo ""
        echo "[数据同步] 使用 scp 同步 src/data/word.db（将覆盖远程同名文件）..."
        scp "$PROJECT_ROOT/src/data/word.db" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/src/data/"

        if [[ -f "$PROJECT_ROOT/src/data/word_history.json" ]]; then
            echo "[数据同步] 同步 src/data/word_history.json（可选）..."
            scp "$PROJECT_ROOT/src/data/word_history.json" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/src/data/"
        fi
    fi
fi

# 2. 远程执行部署
echo ""
echo "[2/3] 连接服务器进行部署..."

ssh "$SERVER_USER@$SERVER_IP" << EOF
    set -e
    cd $REMOTE_DIR
    
    echo "当前目录: \$(pwd)"

    # 检查 Docker 是否安装
    if ! command -v docker &> /dev/null; then
        echo "Docker 未安装，正在安装..."
        curl -fsSL https://get.docker.com | bash
        systemctl start docker
        systemctl enable docker
    fi

    # 配置 Docker 镜像加速 (针对国内网络环境)
    echo "检查 Docker 镜像加速配置..."
    if [ ! -f "/etc/docker/daemon.json" ] || ! grep -q "registry-mirrors" "/etc/docker/daemon.json"; then
        echo "正在配置 Docker 镜像加速器..."
        mkdir -p /etc/docker
        cat > /etc/docker/daemon.json <<END_DAEMON_JSON
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev"
  ]
}
END_DAEMON_JSON
        systemctl daemon-reload
        systemctl restart docker
        echo "Docker 服务已重启"
    fi

    # 检查 Docker Compose
    COMPOSE_CMD=""
    
    # 1. 优先尝试 Docker CLI 插件版 (docker compose)
    if docker compose version &> /dev/null; then
        echo "发现 docker compose 插件，将使用 'docker compose'"
        COMPOSE_CMD="docker compose"
    
    # 2. 其次尝试独立二进制版 (docker-compose)
    elif command -v docker-compose &> /dev/null; then
        echo "发现 docker-compose 二进制文件"
        COMPOSE_CMD="docker-compose"
        # 尝试修复可能缺失的执行权限
        if [ -f "/usr/local/bin/docker-compose" ]; then
            chmod +x /usr/local/bin/docker-compose
        fi
        
    # 3. 如果都没有，则安装 docker-compose
    else
        echo "未找到 Docker Compose，正在安装..."
        curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        COMPOSE_CMD="docker-compose"
    fi

    # 检查配置文件
    if [ ! -f "src/config.py" ]; then
        echo "警告: src/config.py 不存在！"
        if [ -f "src/config.example.py" ]; then
            echo "正在从模板创建 config.py，请稍后手动编辑配置！"
            cp src/config.example.py src/config.py
        fi
    fi

    # 检查 .env（用于 Web 登录/注册开关等环境变量；docker-compose.yml 使用 env_file 读取）
    if [ ! -f ".env" ]; then
        echo "警告: .env 不存在，将创建一个模板文件（请尽快编辑并重启容器）"
        cat > .env <<'END_ENV'
WEB_SECRET_KEY=
WEB_ADMIN_USER=admin
WEB_ADMIN_PASSWORD=
WEB_ALLOW_REGISTER=true
END_ENV
    fi

    echo "停止旧容器..."
    \$COMPOSE_CMD down || true

    echo "构建并启动新容器..."
    \$COMPOSE_CMD up -d --build

    echo "清理无用镜像..."
    docker image prune -f

    echo "部署完成！"
    \$COMPOSE_CMD ps
EOF

echo ""
echo "[3/3] 部署结束！"
echo "Web 面板地址: http://$SERVER_IP/word-web/"
echo "请确保阿里云安全组已开放 80 端口。"
