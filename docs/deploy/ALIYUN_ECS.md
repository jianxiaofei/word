# 阿里云 ECS 发版/部署（Docker Compose）

本文以 ECS（Ubuntu/CentOS 均可）为例，目标是把 Web 面板与定时任务以 Docker Compose 方式发布到服务器，并通过 Nginx 容器对外提供 `http://<IP>/word-web/`。

## 1) 准备服务器

- 创建 ECS：建议 1c2g 起步
- 安全组放行：`22`（SSH）、`80`（HTTP）（如要 HTTPS 再放行 `443`）
- 绑定公网 IP；可选：绑定域名 A 记录到公网 IP

## 2) 推荐发布方式：本地一键部署脚本

你在本地（有代码仓库的机器）执行：

```bash
cd /path/to/word
./scripts/deploy_docker.sh --server-ip <你的ECS公网IP>
```

脚本会：
- 同步代码到远端（默认 `/root/word`）
- 自动安装 Docker / Compose（若缺失）
- `docker compose up -d --build` 重新构建并启动
- 如果远端没有 `.env`，会创建一个模板（需要你补齐密码/密钥）

## 3) 远端配置 `.env`

在 ECS 上编辑：

```bash
cd /root/word
vi .env
```

至少建议设置：

```dotenv
WEB_SECRET_KEY=生成一个足够长的随机串
WEB_ADMIN_USER=admin
WEB_ADMIN_PASSWORD=强密码
WEB_ALLOW_REGISTER=true
```

- `WEB_ALLOW_REGISTER=false` 可关闭普通用户注册入口（保留已有账号登录）。

改完后重启：

```bash
docker compose up -d --build
```

## 4) 访问与验证

- Web 面板：`http://<公网IP>/word-web/`
- 登录：
  - 管理员：使用 `.env` 里的 `WEB_ADMIN_USER/WEB_ADMIN_PASSWORD`
  - 普通用户：访问 `/word-web/register` 注册（若允许）
- 单词绑定：普通用户登录后，在“单词列表”点“绑定”，并在“我的单词”查看

## 5) 建议的上线后配置

- 进入“系统设置”页面：设置 `服务器地址 server_url` 为 `http://<域名或IP>/word-web`（用于邮件交互链接）
- 配置 SMTP / 收件人等参数（推荐在 Web 设置里配置，会写入数据库）

## 6) 更新版本

在本地拉取新代码后，重新执行部署脚本即可：

```bash
./scripts/deploy_docker.sh --server-ip <你的ECS公网IP>
```

## 7) 数据备份（可选但强烈建议）

数据库默认在远端：`/root/word/src/data/word.db`

简单备份：

```bash
cd /root/word
cp src/data/word.db src/data/word.db.bak.$(date +%F_%H%M%S)
```
