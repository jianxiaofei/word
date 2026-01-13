# 方案 C：新机重部署 + 迁移数据（推荐）

适用场景：你不追求整机原样迁移，只希望把服务在新 ECS 上跑起来，并保留旧机器的学习数据/设置。

> 关键结论：本项目的核心数据在 SQLite 数据库文件 `src/data/word.db`。词书、学习进度、Web 设置等都在该 DB 内。

## 0. 前提

- 旧机器仍可 SSH 登录（否则无法拿到最新 `word.db`，只能用历史备份）。
- 新机器可 SSH 登录（示例 IP：`203.0.113.10`）。
- 你的本地电脑能同时 SSH 到旧机和新机（或至少能访问其中之一）。

## 1. 在旧机上备份数据（建议）

在旧机执行：

```bash
cd /root/word
# 停服务，避免拷贝时 DB 正在写入
docker compose down || docker-compose down || true

mkdir -p /root/word_backup
cp -a src/data/word.db "/root/word_backup/word.db.$(date +%F_%H%M%S)"
cp -a src/config.py "/root/word_backup/config.py.$(date +%F_%H%M%S)" 2>/dev/null || true
```

说明：
- `src/data/word.db`：学习记录、词书、设置等
- `src/config.py`：作为配置兜底（大部分配置也会写在 DB settings 表里）

## 2. 把旧机数据拉到本地（推荐路径）

在你的本地（有此仓库代码的机器）执行，把旧机的 DB 拉到本地仓库：

```bash
# 把 <OLD_IP> 替换成旧机器 IP
rsync -avz root@<OLD_IP>:/root/word/src/data/word.db ./src/data/word.db
# 如果旧机还在使用旧版 history 文件，也一并拉取
rsync -avz root@<OLD_IP>:/root/word/src/data/word_history.json ./src/data/word_history.json || true
# 如需同步兜底配置
rsync -avz root@<OLD_IP>:/root/word/src/config.py ./src/config.py || true
```

如果你本地没有 rsync：

```bash
scp root@<OLD_IP>:/root/word/src/data/word.db ./src/data/word.db
scp root@<OLD_IP>:/root/word/src/data/word_history.json ./src/data/word_history.json || true
scp root@<OLD_IP>:/root/word/src/config.py ./src/config.py || true
```

## 3. 部署到新机（包含数据迁移）

在本地仓库目录执行：

```bash
./scripts/deploy_docker.sh --server-ip 203.0.113.10 --sync-data
```

说明：
- 默认部署脚本不会覆盖远程 DB（避免误操作）。
- 加上 `--sync-data` 才会把本地的 `src/data/word.db`、`src/data/word_history.json` 覆盖到新机。

## 4. 安全组/端口

确保新 ECS 安全组至少放通：

- 80（Web 面板）
- 22（SSH）

如你自己改了映射端口，以实际为准。

## 5. 验证

- 打开：http://203.0.113.10/word-web/
- 检查：统计数据、词书列表、学习进度是否与旧机一致
- 检查定时任务容器：

```bash
ssh root@203.0.113.10
cd /root/word
docker compose ps || docker-compose ps
docker logs -n 200 word-scheduler
```

## 6. 切流量（如果你有域名）

- DNS A 记录指向新 IP：`203.0.113.10`
- 或者如果你用的是 EIP：在 EIP 控制台解绑旧实例、绑定新实例（同地域时常用）

## 常见问题

### 旧机欠费已无法登录怎么办？

拿不到最新 DB 的情况下，无法“凭空迁移”。只能：
- 补缴让旧机恢复可登录后按上面步骤取回 `word.db`；或
- 用你之前手头的备份 `word.db` 恢复。

### 迁移后邮件/定时没发？

优先检查：
- 新机时间/时区（容器内已设置 `Asia/Shanghai`）
- Web 设置里 SMTP/收件人是否正确（这些一般在 DB settings 表里）
- 安全组/防火墙是否允许外连 SMTP（部分云厂商默认限制 25 端口；本项目默认用 587/TLS）
