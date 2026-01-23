# 项目优化路线图 (Roadmap)

基于当前重构状态，以下是分阶段的优化建议与实施计划。

## 1. 工程化与稳定性 (优先级：高)

- [ ] **补充单元测试**
    - 目标：确保核心算法（艾宾浩斯复习逻辑）正确性。
    - 行动：在 `tests/` 下新增 `WordSelectorV2`、`WordService`、`StatsService` 覆盖。
    - 工具：`pytest`。

- [x] **Docker 化部署**
    - 行动：已提供 `Dockerfile` + `docker-compose.yml` 与部署脚本。

- [x] **日志与监控**
    - 行动：失败时通过 Webhook 通知（如钉钉/飞书/Server酱）。

- [ ] **健康检查与告警统一**
    - 行动：在定时任务与 Web 端统一健康检查与错误告警输出（结构化日志）。

## 2. 代码与架构优化 (优先级：中)

- [x] **数据存储升级 (SQLite)**
    - 行动：学习记录迁移至 `word.db`，保留旧表兼容。

- [x] **Repository 模式重构**
    - 行动：`core/db/*_repository.py` + `DatabaseManager` 统一入口。

- [x] **路径与配置管理优化**
    - 行动：`pathlib` + `python-dotenv` + `.env`。

- [x] **REST API + Swagger**
    - 行动：`/api/v1/*` + `/api/v1/doc` 在线文档。

- [ ] **权限与角色约束**
    - 目标：管理员页面与普通用户权限分离。
    - 行动：补充 `admin_required` 使用与路由访问控制。

## 3. 功能增强 (优先级：低)

- [x] **Web 端交互增强**
    - 行动：单词状态标记、绑定/取消绑定、我的单词筛选。

- [x] **多词库支持**
    - 行动：支持 TXT/CSV/Excel 导入与激活切换。

- [ ] **AI 内容增强**
    - 行动：接入 LLM API 生成助记提示/短文。

- [ ] **邮件内容个性化**
    - 行动：支持按用户掌握度或难度分层推送。
