#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""艾宾浩斯算法文本可视化（无需matplotlib）"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def print_header(title):
    """打印标题"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def visualize_intervals():
    """可视化复习间隔"""
    print_header("复习间隔可视化")
    
    intervals = [1, 2, 4, 7, 15, 30]
    max_interval = max(intervals)
    
    print("掌握等级  间隔(天)  可视化")
    print("-" * 70)
    
    for i, interval in enumerate(intervals):
        # 计算条形长度（最长50个字符）
        bar_length = int((interval / max_interval) * 50)
        bar = "█" * bar_length
        
        # 颜色标记
        if interval <= 2:
            marker = "🔴"  # 红色 - 短期
        elif interval <= 7:
            marker = "🟡"  # 黄色 - 中期
        else:
            marker = "🟢"  # 绿色 - 长期
        
        print(f"L{i}        {interval:2d}天     {marker} {bar} {interval}天")
    
    print()
    print("图例: 🔴 短期巩固 | 🟡 中期强化 | 🟢 长期记忆")


def visualize_timeline():
    """可视化复习时间轴"""
    print_header("复习时间轴 (2026-01-23 开始)")
    
    intervals = [1, 2, 4, 7, 15, 30]
    start_date = datetime(2026, 1, 23)
    
    cumulative_days = [0]
    for interval in intervals:
        cumulative_days.append(cumulative_days[-1] + interval)
    
    print("时间线:")
    print()
    
    # 打印起点
    print(f"📍 第 0 天  | 2026-01-23 | ⭐ 新学单词")
    print("     ↓ (+1天)")
    
    # 打印每个复习点
    for i, (interval, cum_day) in enumerate(zip(intervals, cumulative_days[1:])):
        review_date = start_date + timedelta(days=cum_day)
        date_str = review_date.strftime("%Y-%m-%d")
        
        if i < len(intervals) - 1:
            next_interval = intervals[i]
            print(f"📌 第{cum_day:2d}天  | {date_str} | L{i} 复习 (已学{cum_day}天)")
            print(f"     ↓ (+{next_interval}天)")
        else:
            print(f"📌 第{cum_day:2d}天  | {date_str} | L{i} 复习 (已学{cum_day}天)")
    
    print()
    print("说明: 每次复习后，下次复习间隔逐渐拉长")


def visualize_memory_curve():
    """可视化记忆曲线"""
    print_header("记忆保持率曲线对比")
    
    intervals = [1, 2, 4, 7, 15, 30]
    cumulative = [0]
    for interval in intervals:
        cumulative.append(cumulative[-1] + interval)
    
    # 生成60天的数据
    print("天数  无复习  有复习  可视化对比")
    print("-" * 70)
    
    key_days = [0, 1, 3, 7, 14, 30, 59]
    
    for day in key_days:
        # 无复习的遗忘曲线 (指数衰减)
        no_review = int(100 * (0.85 ** (day * 0.15)))
        
        # 有复习的记忆保持
        last_review = 0
        for review_day in cumulative[1:]:
            if review_day <= day:
                last_review = review_day
        
        days_since = day - last_review
        base = 95 if last_review > 0 else 100
        with_review = int(base * (0.92 ** (days_since * 0.08)))
        
        # 可视化条形
        bar_no = "█" * (no_review // 2)
        bar_yes = "█" * (with_review // 2)
        
        # 标记复习点
        review_marker = " 🔄" if day in cumulative[1:] else ""
        
        print(f"{day:3d}    {no_review:3d}%   {with_review:3d}%    "
              f"❌{bar_no:<25} ✅{bar_yes:<25}{review_marker}")
    
    print()
    print("图例: ❌ 不复习 | ✅ 艾宾浩斯复习 | 🔄 复习点")
    print()
    print("结论: 30天后，不复习仅剩20%记忆，复习可保持80%以上！")


def visualize_study_load():
    """可视化学习负荷"""
    print_header("30天学习负荷变化 (每天5个新词)")
    
    print("天数  新词  复习  总数  可视化")
    print("-" * 70)
    
    for day in [1, 3, 5, 7, 10, 14, 20, 30]:
        new_words = 5
        
        # 复习词数量逐渐增加
        if day <= 1:
            review = 0
        elif day <= 3:
            review = 5
        elif day <= 7:
            review = 10
        elif day <= 15:
            review = 15
        else:
            review = 20
        
        total = new_words + review
        
        # 可视化
        bar_new = "🆕" * new_words
        bar_review = "🔄" * review
        
        print(f"{day:3d}   {new_words:3d}   {review:3d}   {total:3d}   {bar_new}{bar_review}")
    
    print()
    print("图例: 🆕 新词 | 🔄 复习词")
    print()
    print("说明: 前期以新词为主，后期复习逐渐增多达到平衡")


def visualize_mastery_distribution():
    """可视化掌握度分布"""
    print_header("掌握度分布示例")
    
    # 示例数据
    levels = {
        'L0': 202,
        'L1': 5,
        'L2': 3,
        'L3': 7,
        'L4': 0,
        'L5': 20
    }
    
    max_count = max(levels.values())
    
    print("等级  数量   占比    可视化")
    print("-" * 70)
    
    total = sum(levels.values())
    for level, count in levels.items():
        if count == 0:
            continue
        
        percentage = (count / total) * 100
        bar_length = int((count / max_count) * 40)
        bar = "█" * bar_length
        
        # 等级说明
        descriptions = {
            'L0': '新学/重置',
            'L1': '1天后',
            'L2': '2天后',
            'L3': '4天后',
            'L4': '7天后',
            'L5': '15天后'
        }
        
        desc = descriptions.get(level, '')
        
        print(f"{level}    {count:3d}   {percentage:5.1f}%   {bar} {desc}")
    
    print()
    print(f"总计: {total} 个单词")


def visualize_word_journey():
    """可视化单词学习旅程"""
    print_header("一个单词的完整学习旅程")
    
    print("以单词 'abandon' 为例:\n")
    
    journey = [
        ("第0天", "2026-01-23", "L0", "⭐ 首次学习", "看到生词，了解基本含义"),
        ("第1天", "2026-01-24", "L1", "🔄 第1次复习", "还有印象，快速回顾"),
        ("第3天", "2026-01-26", "L2", "🔄 第2次复习", "开始熟悉，能想起来"),
        ("第7天", "2026-01-30", "L3", "🔄 第3次复习", "比较熟练，偶尔需提示"),
        ("第14天", "2026-02-06", "L4", "🔄 第4次复习", "基本掌握，能正确使用"),
        ("第29天", "2026-02-21", "L5", "🔄 第5次复习", "完全掌握，长期记忆"),
        ("第59天", "2026-03-23", "L6+", "🔄 巩固复习", "持续维护，防止遗忘"),
    ]
    
    for day, date, level, event, status in journey:
        print(f"{day:6s} | {date} | {level:3s} | {event:12s} | {status}")
    
    print()
    print("📊 学习效果:")
    print("   • 前7天:  密集复习，快速巩固")
    print("   • 7-30天: 中期强化，建立长期记忆")
    print("   • 30天后: 定期维护，防止遗忘")


def main():
    """主函数"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "艾宾浩斯算法完整可视化" + " " * 25 + "║")
    print("║" + " " * 15 + "Ebbinghaus Algorithm Visualization" + " " * 17 + "║")
    print("╚" + "═" * 68 + "╝")
    
    visualize_intervals()
    visualize_timeline()
    visualize_memory_curve()
    visualize_study_load()
    visualize_mastery_distribution()
    visualize_word_journey()
    
    print()
    print("=" * 70)
    print("✨ 可视化完成！")
    print("=" * 70)
    print()
    print("💡 核心理念:")
    print("   1. 遗忘是自然规律，科学复习能对抗遗忘")
    print("   2. 间隔重复是最有效的长期记忆方法")
    print("   3. 艾宾浩斯曲线经过百年验证，科学可靠")
    print()
    print("🎯 使用建议:")
    print("   • 每天坚持学习新词 + 复习旧词")
    print("   • 不要跳过复习，即使觉得已经记住")
    print("   • 遇到不会的单词标记'不认识'，重新学习")
    print("   • 相信科学，坚持30天就能看到效果")
    print()


if __name__ == '__main__':
    main()
