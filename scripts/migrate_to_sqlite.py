# -*- coding: utf-8 -*-
"""迁移脚本：将 JSON 历史记录迁移到 SQLite"""

import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import DatabaseManager

def migrate():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(project_root, 'src', 'data', 'word_history.json')
    
    if not os.path.exists(json_path):
        print(f"未找到 JSON 文件: {json_path}，无需迁移。")
        return

    print(f"正在读取 JSON 文件: {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取 JSON 失败: {e}")
        return

    words_data = data.get('words', {})
    if not words_data:
        print("JSON 中没有单词记录。")
        return

    db = DatabaseManager()
    print(f"开始迁移 {len(words_data)} 条记录到 SQLite...")
    
    count = 0
    for idx_str, info in words_data.items():
        try:
            idx = int(idx_str)
            db.add_word(
                word_index=idx,
                word=info.get('word', ''),
                first_learned=info.get('first_learned'),
                last_review=info.get('last_review'),
                next_review=info.get('next_review'),
                review_count=info.get('review_count', 0),
                mastery_level=info.get('mastery_level', 0)
            )
            count += 1
            if count % 100 == 0:
                print(f"已处理 {count} 条...")
        except Exception as e:
            print(f"迁移记录 {idx_str} 失败: {e}")

    print(f"迁移完成！共成功迁移 {count} 条记录。")
    
    # 重命名旧文件
    backup_path = json_path + '.bak'
    os.rename(json_path, backup_path)
    print(f"已将原 JSON 文件重命名为: {backup_path}")

if __name__ == '__main__':
    migrate()
