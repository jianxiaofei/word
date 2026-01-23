# Core 模块优化重构方案

## 当前问题

### 1. database.py (724 行) - 臃肿
**问题：**
- 单一类承担太多职责（用户、单词、词书、设置、绑定关系）
- 违反单一职责原则
- 难以维护和测试
- 方法过多（40+ 个方法）

**当前结构：**
```
DatabaseManager (724 lines)
├── 数据库连接管理 (3 methods)
├── 用户认证 (3 methods)
├── 用户-单词绑定 (4 methods)
├── 迁移功能 (1 method)
├── 设置管理 (5 methods)
├── 词书管理 (5 methods)
├── 单词管理 (10+ methods)
└── 历史记录 (3 methods)
```

### 2. 其他文件相对合理
- email_sender.py (158 行) - 合理
- word_selector.py (156 行) - 合理
- example_fetcher.py (252 行) - 略大但职责单一
- word_parser.py (102 行) - 合理
- notifier.py (68 行) - 合理

## 重构方案

### 方案一：按 Repository 模式拆分（推荐）

```
src/core/db/
├── __init__.py                 # 统一导出接口
├── connection.py               # 数据库连接管理
├── base_repository.py          # Repository 基类
├── user_repository.py          # 用户相关操作 (~150 行)
├── word_repository.py          # 单词相关操作 (~200 行)
├── book_repository.py          # 词书相关操作 (~100 行)
├── settings_repository.py      # 设置相关操作 (~80 行)
├── binding_repository.py       # 用户-单词绑定 (~100 行)
└── manager.py                  # 统一管理器（兼容旧接口）
```

**优点：**
- 职责清晰，每个类只负责一类数据
- 易于测试和维护
- 遵循 SOLID 原则
- 可以逐步迁移，保持向后兼容

**UserRepository 示例：**
```python
class UserRepository(BaseRepository):
    def create_user(self, username: str, password: str) -> Tuple[bool, str]
    def get_user_by_username(self, username: str) -> Optional[Dict]
    def verify_user(self, username: str, password: str) -> Optional[Dict]
    def get_user_by_id(self, user_id: int) -> Optional[Dict]
```

**兼容层（manager.py）：**
```python
class DatabaseManager:
    """向后兼容的统一管理器"""
    def __init__(self, db_path: str = None):
        self._get_conn = lambda: get_connection(db_path)
        self.users = UserRepository(self._get_conn)
        self.words = WordRepository(self._get_conn)
        self.books = BookRepository(self._get_conn)
        self.settings = SettingsRepository(self._get_conn)
        self.bindings = BindingRepository(self._get_conn)
    
    # 委托方法保持向后兼容
    def create_user(self, *args, **kwargs):
        return self.users.create_user(*args, **kwargs)
    
    def get_all_books(self):
        return self.books.get_all()
```

### 方案二：保持单文件，重构为内部类

```python
class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.users = self.UserOperations(self)
        self.words = self.WordOperations(self)
        self.books = self.BookOperations(self)
    
    class UserOperations:
        def __init__(self, manager):
            self.manager = manager
        # 用户相关方法
    
    class WordOperations:
        # 单词相关方法
```

**优点：**
- 改动较小
- 保持向后兼容

**缺点：**
- 文件仍然很大
- 不利于独立测试

## 迁移策略

### 阶段 1：创建新结构（不影响现有代码）
1. 创建 src/core/db/ 目录
2. 实现各个 Repository 类
3. 实现兼容层 DatabaseManager
4. 编写单元测试

### 阶段 2：逐步迁移
1. 新功能使用新接口
2. 旧代码保持不变
3. 逐个模块迁移到新接口

### 阶段 3：清理旧代码
1. 所有代码迁移完成后
2. 删除 database.py 中的旧方法
3. 保留兼容层或完全切换到新接口

## 其他优化建议

### 1. example_fetcher.py (252 行)
考虑拆分：
- FetcherBase - 基础抓取逻辑
- CambridgeFetcher - 剑桥词典
- MerriamWebsterFetcher - 韦氏词典

### 2. 添加类型提示和文档
所有方法添加完整的类型提示和 docstring

### 3. 统一错误处理
创建自定义异常类，统一错误处理方式

### 4. 添加日志
在关键操作添加日志记录

## 建议

**当前阶段：**
由于系统正在使用中，建议：
1. ✅ **不要现在重构** - 先确保现有功能正常运行
2. ✅ 在本地环境完整测试所有功能
3. ✅ 部署到生产环境
4. ✅ 收集实际使用反馈

**下一阶段：**
1. 创建详细的测试用例
2. 在独立分支进行重构
3. 充分测试后再合并

**优先级：**
- 🔴 高：确保现有功能稳定运行
- 🟡 中：重构 database.py（可以等稳定后）
- 🟢 低：优化其他文件

## 总结

database.py 确实臃肿，应该重构。但考虑到：
1. 你刚完成 API 集成和多个功能修复
2. 系统还在本地测试阶段
3. 重构是大工程，需要充分测试

**建议：先让系统稳定运行一段时间，再进行重构。**

如果你确认要现在重构，我可以帮你完成。
