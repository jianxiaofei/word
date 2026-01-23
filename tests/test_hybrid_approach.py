#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试混合方案：24小时自动标记功能"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.word_selector import WordSelectorV2
from src.core.db.manager import DatabaseManager


def test_hybrid_approach():
    """测试混合方案功能"""
    
    print("=" * 70)
    print("混合方案功能测试")
    print("=" * 70)
    print()
    
    selector = WordSelectorV2()
    db = DatabaseManager()
    
    # 1. 测试发送标记
    print("1. 测试发送标记功能")
    print("-" * 70)
    
    today = datetime.now().date().isoformat()
    yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
    
    # 获取一些到期单词
    due_words = db.get_words_for_review(today)
    
    if not due_words:
        print("⚠ 没有到期单词可供测试")
        return
    
    test_words = due_words[:3]  # 取3个单词测试
    test_word_ids = [w['id'] for w in test_words]
    
    print(f"选择 {len(test_words)} 个单词进行测试:")
    for w in test_words:
        print(f"  - {w['word']}: next_review={w['next_review']}, sent_date={w.get('sent_date', 'None')}")
    
    # 模拟昨天发送
    print(f"\n模拟标记这些单词在昨天({yesterday})已发送...")
    db.words.mark_words_sent(test_word_ids, yesterday)
    
    # 验证标记
    print("\n验证发送标记:")
    for word_id in test_word_ids:
        word = db.get_word_by_id(word_id)
        print(f"  - {word['word']}: sent_date={word.get('sent_date')}")
    
    print("\n✓ 发送标记功能正常")
    print()
    
    # 2. 测试自动标记
    print("2. 测试自动标记功能")
    print("-" * 70)
    
    print(f"查找昨天({yesterday})之前发送但未反馈的单词...")
    words_before = db.words.get_words_sent_before(today)
    
    print(f"找到 {len(words_before)} 个需要自动标记的单词")
    if words_before:
        for w in words_before[:5]:
            print(f"  - {w['word']}: sent_date={w.get('sent_date')}, last_review={w.get('last_review')}")
    
    # 执行自动标记
    print(f"\n执行自动标记...")
    marked_count = selector.auto_mark_sent_words(hours=24)
    
    print(f"✓ 已自动标记 {marked_count} 个单词")
    print()
    
    # 3. 验证标记效果
    print("3. 验证标记效果")
    print("-" * 70)
    
    for word_id in test_word_ids:
        word = db.get_word_by_id(word_id)
        print(f"\n单词: {word['word']}")
        print(f"  sent_date: {word.get('sent_date')} (应该被清空)")
        print(f"  last_review: {word['last_review']} (应该是今天)")
        print(f"  next_review: {word['next_review']} (应该已更新)")
        print(f"  mastery_level: L{word['mastery_level']}")
        
        # 验证
        assert word.get('sent_date') is None, "sent_date 应该被清空"
        assert word['last_review'] == today, "last_review 应该是今天"
    
    print("\n✓ 所有验证通过！")
    print()
    
    # 4. 测试用户主动反馈
    print("4. 测试用户主动反馈优先级")
    print("-" * 70)
    
    # 再次标记发送
    more_words = db.get_words_for_review(today)
    if more_words:
        test_word = more_words[0]
        print(f"测试单词: {test_word['word']}")
        
        # 标记为昨天发送
        db.words.mark_words_sent([test_word['id']], yesterday)
        print(f"  标记为昨天发送: sent_date={yesterday}")
        
        # 用户标记为"不认识"
        print("  用户主动标记为'不认识'...")
        selector.mark_unknown(test_word['id'])
        
        # 验证：sent_date应该被清空，mastery_level应该重置为0
        updated_word = db.get_word_by_id(test_word['id'])
        print(f"  sent_date: {updated_word.get('sent_date')} (应该被清空)")
        print(f"  mastery_level: L{updated_word['mastery_level']} (应该重置为L0)")
        print(f"  next_review: {updated_word['next_review']} (应该是明天)")
        
        assert updated_word.get('sent_date') is None, "用户反馈后sent_date应该被清空"
        assert updated_word['mastery_level'] == 0, "标记不认识应该重置为L0"
        
        print("\n✓ 用户主动反馈优先于自动标记")
    
    print()
    print("=" * 70)
    print("✅ 混合方案所有测试通过！")
    print("=" * 70)
    print()
    
    # 5. 输出使用说明
    print("💡 混合方案工作流程:")
    print()
    print("1. 发送邮件时:")
    print("   - 新单词：立即更新为学习中状态")
    print("   - 复习单词：标记 sent_date=今天，等待反馈")
    print()
    print("2. 用户反馈（24小时内）:")
    print("   - 点击'认识'：正常推进复习进度，清除sent_date")
    print("   - 点击'不认识'：重置为L0，清除sent_date")
    print()
    print("3. 24小时后未反馈:")
    print("   - 自动按'认识'处理")
    print("   - 更新复习日期")
    print("   - 清除sent_date")
    print()
    print("✨ 优势:")
    print("   ✓ 鼓励用户主动反馈")
    print("   ✓ 避免单词累积")
    print("   ✓ 系统自动容错")
    print("   ✓ 用户体验友好")


if __name__ == '__main__':
    try:
        test_hybrid_approach()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
