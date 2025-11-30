import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import DatabaseManager
from src.core.word_parser import WordParser

def main():
    print("开始执行 V2 数据库迁移...")
    
    # 1. 初始化数据库 (创建新表)
    db = DatabaseManager()
    
    # 2. 解析默认词库 (用于迁移)
    word_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'data', 'CET4_edited.txt')
    if os.path.exists(word_file):
        print(f"读取默认词库: {word_file}")
        parser = WordParser(word_file)
        default_words = parser.parse()
        
        # 3. 执行迁移
        db.migrate_v1_to_v2(default_words)
    else:
        print("未找到默认词库文件，跳过数据迁移。")
        
    print("迁移完成！")

if __name__ == '__main__':
    main()
