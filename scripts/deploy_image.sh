#!/bin/bash
# Docker 镜像式部署脚本（推荐）
# 本地构建镜像，传输到服务器运行

set -euo pipefail

usage() {
    cat << 'USAGE'
用法:
    ./scripts/deploy_image.sh --server-ip <ip> [选项]

参数:
  --server-ip       目标服务器 IP（必填）
  --server-user     SSH 用户（默认: root）
  --remote-dir      远程部署目录（默认: /root/word）
  --image-tag       镜像版本标签（默认: latest）
  --use-registry    使用镜像仓库（需先配置 REGISTRY 环境变量）

示例:
    # 本地构建并传输镜像到服务器
    ./scripts/deploy_image.sh --server-ip 121.196.225.91
    
    # 指定版本号
    ./scripts/deploy_image.sh --server-ip 121.196.225.91 --image-tag v1.0.0
    
    # 使用镜像仓库（需先 docker login）
    export REGISTRY=registry.cn-hangzhou.aliyuncs.com/yourname
    ./scripts/deploy_image.sh --server-ip 121.196.225.91 --use-registry

USAGE
}

SERVER_IP=""
SERVER_USER="root"
REMOTE_DIR="/root/word"
IMAGE_TAG="latest"
USE_REGISTRY=0
REGISTRY="${REGISTRY:-}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --server-ip)
            SERVER_IP="${2:-}"; shift 2 ;;
        --server-user)
            SERVER_USER="${2:-}"; shift 2 ;;
        --remote-dir)
            REMOTE_DIR="${2:-}"; shift 2 ;;
        --image-tag)
            IMAGE_TAG="${2:-}"; shift 2 ;;
        --use-registry)
            USE_REGISTRY=1; shift 1 ;;
        -h|--help)
            usage; exit 0 ;;
        *)
            echo "未知参数: $1" >&2
            usage
            exit 2
            ;;
    esac
done

if [[ -z "$SERVER_IP" ]]; then
    echo "缺少必填参数: --server-ip" >&2
    usage
    exit 2
fi

if [[ $USE_REGISTRY -eq 1 && -z "$REGISTRY" ]]; then
    echo "错误: 使用镜像仓库模式需要设置 REGISTRY 环境变量" >&2
    echo "示例: export REGISTRY=registry.cn-hangzhou.aliyuncs.com/yourname" >&2
    exit 2
fi

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
IMAGE_NAME="word-app"

if [[ $USE_REGISTRY -eq 1 ]]; then
    FULL_IMAGE_NAME="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
else
    FULL_IMAGE_NAME="$IMAGE_NAME:$IMAGE_TAG"
fi

echo "======================================"
echo "单词系统 - Docker 镜像式部署"
echo "======================================"
echo "目标服务器: $SERVER_USER@$SERVER_IP"
echo "镜像名称: $FULL_IMAGE_NAME"
echo "部署模式: $(if [[ $USE_REGISTRY -eq 1 ]]; then echo '镜像仓库'; else echo '文件传输'; fi)"
echo "======================================"

# 1. 本地构建镜像
echo ""
echo "[1/4] 本地构建 Docker 镜像..."
cd "$PROJECT_ROOT"

# 检测服务器架构
echo "检测服务器架构..."
SERVER_ARCH=$(ssh "$SERVER_USER@$SERVER_IP" "uname -m")
if [[ "$SERVER_ARCH" == "x86_64" ]]; then
    PLATFORM="linux/amd64"
elif [[ "$SERVER_ARCH" == "aarch64" ]]; then
    PLATFORM="linux/arm64"
else
    PLATFORM="linux/amd64"  # 默认
fi

echo "服务器架构: $SERVER_ARCH, 构建平台: $PLATFORM"

docker build --platform "$PLATFORM" -t "$FULL_IMAGE_NAME" .

echo "✓ 镜像构建完成"

# 2. 传输镜像
if [[ $USE_REGISTRY -eq 1 ]]; then
    echo ""
    echo "[2/4] 推送镜像到仓库..."
    docker push "$FULL_IMAGE_NAME"
    echo "✓ 镜像推送完成"
else
    echo ""
    echo "[2/4] 保存镜像为文件..."
    IMAGE_FILE="/tmp/word-app-${IMAGE_TAG}.tar"
    docker save -o "$IMAGE_FILE" "$FULL_IMAGE_NAME"
    
    echo "传输镜像到服务器..."
    scp "$IMAGE_FILE" "$SERVER_USER@$SERVER_IP:/tmp/"
    
    echo "服务器加载镜像..."
    ssh "$SERVER_USER@$SERVER_IP" "docker load -i /tmp/word-app-${IMAGE_TAG}.tar && rm /tmp/word-app-${IMAGE_TAG}.tar"
    
    # 如果不是 latest 标签，额外打一个 latest 标签
    if [[ "$IMAGE_TAG" != "latest" ]]; then
        echo "为镜像打 latest 标签..."
        ssh "$SERVER_USER@$SERVER_IP" "docker tag word-app:${IMAGE_TAG} word-app:latest"
    fi
    
    rm "$IMAGE_FILE"
    echo "✓ 镜像传输完成"
fi

# 3. 同步配置文件
echo ""
echo "[3/4] 同步配置文件..."
ssh "$SERVER_USER@$SERVER_IP" "mkdir -p '$REMOTE_DIR' '$REMOTE_DIR/volumes/config' '$REMOTE_DIR/volumes/data' '$REMOTE_DIR/volumes/logs' '$REMOTE_DIR/backups'"

# 创建生产环境的 docker-compose.yml
cat > /tmp/docker-compose.prod.yml << 'EOF'
services:
  # Web 统计面板服务
  web:
    image: word-app:latest
    pull_policy: never
    container_name: word-web
    restart: unless-stopped
    expose:
      - "5000"
    env_file:
      - .env
    volumes:
      # 挂载配置文件
      - ./volumes/config/config.py:/app/src/config/config.py:ro
      # 挂载数据目录和日志
      - ./volumes/data:/app/src/data
      - ./volumes/logs:/app/logs
    environment:
      - FLASK_APP=src/web/app.py
      - FLASK_DEBUG=0
      - TZ=Asia/Shanghai
      - WEB_SECRET_KEY=${WEB_SECRET_KEY:-}
      - WEB_ADMIN_USER=${WEB_ADMIN_USER:-admin}
      - WEB_ADMIN_PASSWORD=${WEB_ADMIN_PASSWORD:-}
      - WEB_ALLOW_REGISTER=${WEB_ALLOW_REGISTER:-true}
    command: python -m flask run --host=0.0.0.0

  # 定时任务调度服务
  scheduler:
    image: word-app:latest
    pull_policy: never
    container_name: word-scheduler
    restart: unless-stopped
    depends_on:
      - web
    env_file:
      - .env
    volumes:
      # 挂载配置文件
      - ./volumes/config/config.py:/app/src/config/config.py:ro
      - ./volumes/data:/app/src/data
      - ./volumes/logs:/app/logs
    environment:
      - SCHEDULE_TIME=07:30
      - TZ=Asia/Shanghai
    command: python scripts/docker_scheduler.py
EOF

# 上传配置文件
scp /tmp/docker-compose.prod.yml "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/docker-compose.yml"
rm /tmp/docker-compose.prod.yml

# 上传必要的配置文件（如果不存在）
if [[ -f "$PROJECT_ROOT/src/config/config.py" ]]; then
    ssh "$SERVER_USER@$SERVER_IP" "test -f '$REMOTE_DIR/volumes/config/config.py' || echo '需要配置文件'"
    read -p "是否上传 src/config/config.py？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        scp "$PROJECT_ROOT/src/config/config.py" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/volumes/config/config.py"
    fi
fi

# 检查 .env
ssh "$SERVER_USER@$SERVER_IP" << EOF
    cd $REMOTE_DIR
    if [ ! -f ".env" ]; then
        echo "创建 .env 模板..."
        cat > .env <<'END_ENV'
WEB_SECRET_KEY=
WEB_ADMIN_USER=admin
WEB_ADMIN_PASSWORD=
WEB_ALLOW_REGISTER=true
END_ENV
        echo "⚠️  请编辑 .env 文件配置管理员密码！"
    fi
EOF

echo "✓ 配置文件同步完成"

# 4. 启动容器
echo ""
echo "[4/4] 启动容器..."
ssh "$SERVER_USER@$SERVER_IP" << EOF
    set -e
    cd $REMOTE_DIR
    
    # 检查 Docker Compose 命令
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo "错误: 未找到 Docker Compose" >&2
        exit 1
    fi
    
    echo "停止旧容器..."
    \$COMPOSE_CMD down || true
    
    echo "启动新容器..."
    \$COMPOSE_CMD up -d
    
    echo "清理无用镜像..."
    docker image prune -f
    
    echo ""
    echo "✓ 部署完成！"
    \$COMPOSE_CMD ps
EOF

echo ""
echo "======================================"
echo "部署成功！"
echo "Web 面板: http://$SERVER_IP/word-web/"
echo "======================================"
