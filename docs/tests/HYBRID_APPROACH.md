# 混合方案实现说明

## 🎯 方案概述

**混合方案**结合了用户主动反馈和系统自动容错，是最佳的单词复习机制。

---

## ✨ 核心机制

### 1. 发送邮件时

```
┌─────────────┐
│  选择单词    │
│ 5新 + 5复习  │
└──────┬──────┘
       │
       ├─→ 新单词
       │   ├─ 立即更新status=1
       │   ├─ 设置first_learned=今天
       │   └─ 设置next_review=明天
       │
       └─→ 复习单词
           ├─ 标记sent_date=今天
           ├─ 不更新next_review
           └─ 等待用户反馈
```

### 2. 用户反馈（24小时内）

```
用户收到邮件
       │
       ├─→ 点击"认识"
       │   ├─ review_count + 1
       │   ├─ mastery_level + 1
       │   ├─ 更新next_review
       │   └─ 清除sent_date ✓
       │
       ├─→ 点击"不认识"
       │   ├─ mastery_level → L0
       │   ├─ next_review → 明天
       │   └─ 清除sent_date ✓
       │
       └─→ 不点击（忙/忘记）
           ├─ sent_date保持不变
           └─ 等待自动处理...
```

### 3. 24小时后自动处理

```
每天运行main.py时
       │
       ▼
┌─────────────────┐
│ auto_mark_sent  │
│   _words()      │
└────────┬────────┘
         │
         ▼
查询: sent_date <= 昨天
  AND last_review != sent_date
         │
         ▼
找到未反馈单词
         │
         ├─→ 自动调用mark_reviewed()
         │   ├─ 按"认识"处理
         │   ├─ 更新复习进度
         │   └─ 清除sent_date
         │
         └─→ 记录日志
             "已自动标记 N 个单词"
```

---

## 📊 数据流

### 数据库字段

**words表新增**:
```sql
sent_date DATE  -- 发送日期标记
```

**状态说明**:
- `sent_date = NULL`: 未发送或已反馈
- `sent_date = 昨天`: 昨天发送，待反馈
- `sent_date != last_review`: 已发送未反馈

### 核心SQL

**标记发送**:
```sql
UPDATE words 
SET sent_date = '2026-01-23'
WHERE id IN (1, 2, 3, 4, 5)
```

**查找待自动标记**:
```sql
SELECT * FROM words 
WHERE sent_date IS NOT NULL 
AND sent_date <= '2026-01-22'
AND (last_review IS NULL OR last_review != sent_date)
AND status = 1
```

**清除发送标记**:
```sql
UPDATE words 
SET sent_date = NULL
WHERE id = ?
```

---

## 🔧 实现细节

### 1. 数据库Schema

**文件**: [src/core/db/schema.py](../src/core/db/schema.py)

```python
# 添加sent_date字段
cursor.execute('PRAGMA table_info(words)')
word_cols = {row[1] for row in cursor.fetchall()}
if 'sent_date' not in word_cols:
    cursor.execute('ALTER TABLE words ADD COLUMN sent_date DATE')
```

### 2. WordRepository方法

**文件**: [src/core/db/word_repository.py](../src/core/db/word_repository.py)

```python
def mark_words_sent(self, word_ids: List[int], sent_date: str):
    """标记单词已发送"""
    
def get_words_sent_before(self, before_date: str) -> List[Dict]:
    """获取待自动标记的单词"""
    
def clear_sent_date(self, word_id: int):
    """清除发送标记"""
```

### 3. WordSelector方法

**文件**: [src/core/word_selector.py](../src/core/word_selector.py)

```python
def select_words(self, new_count: int, review_count: int):
    """选择单词时标记sent_date"""
    # ... 选择逻辑 ...
    
    # 标记复习单词已发送
    today = datetime.now().date().isoformat()
    review_word_ids = [w['id'] for w in review_words]
    if review_word_ids:
        self.db.words.mark_words_sent(review_word_ids, today)
    
    return new_words, review_words

def auto_mark_sent_words(self, hours: int = 24) -> int:
    """自动标记超时未反馈的单词"""
    before_date = (datetime.now().date() - timedelta(days=1)).isoformat()
    words_to_mark = self.db.words.get_words_sent_before(before_date)
    
    marked_count = 0
    for word in words_to_mark:
        self.mark_reviewed(word['id'])
        self.db.words.clear_sent_date(word['id'])
        marked_count += 1
    
    return marked_count

def mark_reviewed(self, word_id: int):
    """标记已复习时清除sent_date"""
    # ... 更新进度 ...
    self.db.words.clear_sent_date(word_id)

def mark_unknown(self, word_id: int):
    """标记不认识时也清除sent_date"""
    # ... 重置等级 ...
    self.db.words.clear_sent_date(word_id)
```

### 4. Main程序集成

**文件**: [src/main.py](../src/main.py)

```python
def main():
    # 0. 自动标记超时单词
    logger.info("检查需要自动标记的单词...")
    selector = WordSelectorV2()
    auto_marked = selector.auto_mark_sent_words(hours=24)
    if auto_marked > 0:
        logger.info(f"✓ 已自动标记 {auto_marked} 个超时未反馈的单词")
    
    # 1. 选择单词（会自动标记sent_date）
    new_words, review_words = selector.select_words(...)
    
    # 2. 发送邮件
    # ...
```

### 5. 邮件模板更新

**文件**: [src/data/email_template.html](../src/data/email_template.html)

```html
<!-- 修正URL路径 -->
<a href="{{ server_url }}/words/mark/{{ word.id }}?action=known">
    ✓ 认识 / 已复习
</a>
<a href="{{ server_url }}/words/mark/{{ word.id }}?action=unknown">
    ✗ 不认识 / 重置
</a>

<!-- 添加提示 -->
<div style="...">
    💡 请点击按钮反馈学习效果，24小时内未反馈将自动按"认识"处理
</div>
```

---

## 🎭 典型场景

### 场景1: 用户及时反馈

```
Day 1 07:30  发送邮件（5新词 + 5复习词）
         ↓
Day 1 08:00  用户打开邮件
         ↓   点击3个"认识"、2个"不认识"
         ↓   → 这5个单词的sent_date被清除
         ↓   → 复习进度正常推进
         ↓
Day 2 07:30  自动标记检查
         ↓   → 找到0个待处理单词（都已反馈）
         ↓   → 继续发送新邮件
```

### 场景2: 用户部分反馈

```
Day 1 07:30  发送邮件（5新词 + 5复习词）
         ↓
Day 1 晚上   用户只标记了2个
         ↓   → 2个单词sent_date被清除
         ↓   → 3个单词sent_date=Day1
         ↓
Day 2 07:30  自动标记检查
         ↓   → 找到3个待处理单词
         ↓   → 自动标记为"已复习"
         ↓   → 清除sent_date
```

### 场景3: 用户忘记反馈

```
Day 1 07:30  发送邮件（5新词 + 5复习词）
         ↓
Day 1 全天   用户太忙，没有打开邮件
         ↓   → 5个复习词sent_date=Day1
         ↓
Day 2 07:30  自动标记检查
         ↓   → 找到5个待处理单词
         ↓   → 全部自动标记为"已复习"
         ↓   → 清除sent_date
         ↓   → 系统正常运转，不累积
```

---

## ⚖️ 优势对比

| 特性 | 纯手动反馈 | 自动标记 | **混合方案** |
|-----|----------|---------|------------|
| 用户参与 | 必须 ❌ | 不需要 ⚠️ | 鼓励但不强制 ✅ |
| 防止累积 | 会累积 ❌ | 不累积 ✅ | 不累积 ✅ |
| 反馈准确 | 最准确 ✅ | 不准确 ❌ | 较准确 ✅ |
| 容错能力 | 无 ❌ | 完全 ✅ | 平衡 ✅ |
| 用户体验 | 差（强制） ❌ | 好（无压力） ✅ | 最佳 ✅ |
| 主动回忆 | 充分 ✅ | 缺失 ❌ | 保留 ✅ |
| 系统稳定 | 不稳定 ❌ | 稳定 ✅ | 稳定 ✅ |

---

## 📈 预期效果

### 减少累积

**之前**:
- 214个到期单词持续累积
- 每天+5新到期，-5处理
- 净增长取决于用户反馈率

**之后**:
- 用户反馈的立即处理
- 未反馈的24小时后自动处理
- 累积量控制在0-10个以内

### 提升体验

**用户感受**:
1. 看到提示"24小时内反馈"→ 有缓冲时间，不焦虑
2. 想反馈时点击按钮 → 有参与感，记忆更深
3. 忘记反馈也不影响 → 系统自动处理，无负担

### 数据质量

**掌握度评估**:
- 用户主动标记的 → 准确反映真实掌握度
- 自动标记的 → 至少表示"看过邮件"
- 比纯自动标记更可信
- 比纯手动无容错更实用

---

## 🔍 监控指标

### 建议跟踪

1. **反馈率**: `主动反馈数 / 发送数`
2. **自动标记率**: `自动标记数 / 发送数`
3. **平均反馈时长**: `反馈时间 - 发送时间`
4. **累积单词数**: `sent_date不为空的单词数`

### 健康标准

- 反馈率 > 50%: 优秀
- 反馈率 30-50%: 良好
- 反馈率 < 30%: 需优化提示

- 累积单词 < 10: 正常
- 累积单词 10-20: 注意
- 累积单词 > 20: 需检查

---

## 🚀 未来优化

### 短期

1. Web端添加"批量反馈"功能
2. 邮件中添加"一键全部已复习"按钮
3. 移动端推送通知

### 中期

1. 根据用户历史反馈率调整自动标记时间
2. AI预测用户掌握度
3. 个性化复习间隔

### 长期

1. 语音反馈支持
2. 游戏化元素
3. 社交学习功能

---

## ✅ 验证结果

已通过完整测试：[test_hybrid_approach.py](./test_hybrid_approach.py)

**测试覆盖**:
- ✅ 发送标记功能
- ✅ 自动标记功能
- ✅ 用户反馈优先级
- ✅ sent_date清除机制
- ✅ 复习进度更新

**测试输出**:
```
✅ 混合方案所有测试通过！
已自动标记 6 个超时未反馈的单词
```

---

## 📚 相关文档

- [交互问题分析](./INTERACTION_ISSUE.md)
- [算法验证总结](./VALIDATION_SUMMARY.md)
- [项目README](../README.md)

---

**实现完成**: 2026-01-23  
**方案设计**: AI Assistant  
**状态**: ✅ 测试通过，可投入使用
