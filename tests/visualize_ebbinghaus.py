#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""艾宾浩斯复习曲线可视化"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


def plot_review_intervals():
    """绘制复习间隔图"""
    intervals = [1, 2, 4, 7, 15, 30]
    levels = [f'L{i}' for i in range(len(intervals))]
    
    # 计算累计天数
    cumulative_days = [0]
    for i, interval in enumerate(intervals):
        cumulative_days.append(cumulative_days[-1] + interval)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # === 图1: 复习间隔条形图 ===
    colors = ['#FF6B6B', '#FFA07A', '#FFD93D', '#6BCF7F', '#4ECDC4', '#95E1D3']
    bars = ax1.bar(levels, intervals, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # 添加数值标签
    for i, (bar, interval) in enumerate(zip(bars, intervals)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{interval}天',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax1.set_xlabel('掌握等级', fontsize=14, fontweight='bold')
    ax1.set_ylabel('复习间隔 (天)', fontsize=14, fontweight='bold')
    ax1.set_title('艾宾浩斯复习间隔设置', fontsize=16, fontweight='bold', pad=20)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(0, max(intervals) * 1.2)
    
    # === 图2: 复习时间轴 ===
    start_date = datetime(2026, 1, 23)
    
    # 绘制时间轴
    y_pos = 1
    ax2.axhline(y=y_pos, color='gray', linewidth=2, alpha=0.5)
    
    # 标记每次复习点
    for i, (level, cum_day) in enumerate(zip(levels, cumulative_days[1:])):
        review_date = start_date + timedelta(days=cum_day)
        
        # 绘制复习点
        ax2.plot(cum_day, y_pos, 'o', markersize=15, color=colors[i], 
                markeredgecolor='black', markeredgewidth=2, zorder=3)
        
        # 添加日期标签
        ax2.text(cum_day, y_pos + 0.15, 
                f'{level}\n{review_date.strftime("%m-%d")}\n({cum_day}天)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 绘制间隔箭头
        if i > 0:
            prev_day = cumulative_days[i]
            interval = intervals[i-1]
            ax2.annotate('', xy=(cum_day, y_pos-0.05), xytext=(prev_day, y_pos-0.05),
                        arrowprops=dict(arrowstyle='<->', lw=2, color=colors[i-1], alpha=0.6))
            ax2.text((prev_day + cum_day) / 2, y_pos - 0.25,
                    f'+{interval}天', ha='center', va='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 标记起点
    ax2.plot(0, y_pos, 's', markersize=15, color='#FF4757', 
            markeredgecolor='black', markeredgewidth=2, zorder=3)
    ax2.text(0, y_pos + 0.15, '新学\n01-23\n(第0天)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax2.set_xlabel('学习天数', fontsize=14, fontweight='bold')
    ax2.set_title('单词复习时间轴 (示例: 2026-01-23开始)', fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlim(-3, cumulative_days[-1] + 5)
    ax2.set_ylim(0.5, 1.5)
    ax2.set_yticks([])
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    # 保存图片
    output_path = os.path.join(os.path.dirname(__file__), 'ebbinghaus_curve.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 复习曲线图已保存: {output_path}")
    
    return output_path


def plot_mastery_progression():
    """绘制掌握度进展图"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 数据
    intervals = [1, 2, 4, 7, 15, 30]
    cumulative = [0]
    for interval in intervals:
        cumulative.append(cumulative[-1] + interval)
    
    # 模拟记忆保持率曲线
    days = list(range(0, cumulative[-1] + 10))
    
    # 没有复习的遗忘曲线 (指数衰减)
    no_review = [100 * (0.85 ** (d * 0.15)) for d in days]
    
    # 有复习的记忆曲线
    memory_with_review = []
    for d in days:
        # 找到最近的复习点
        last_review = 0
        for review_day in cumulative[1:]:
            if review_day <= d:
                last_review = review_day
        
        # 从最近复习点开始计算衰减
        days_since_review = d - last_review
        base_memory = 95 if last_review > 0 else 100
        retention = base_memory * (0.92 ** (days_since_review * 0.08))
        memory_with_review.append(retention)
    
    # 绘制曲线
    ax.plot(days, no_review, '--', color='#FF6B6B', linewidth=2, 
            label='无复习 (自然遗忘)', alpha=0.7)
    ax.plot(days, memory_with_review, '-', color='#4ECDC4', linewidth=3,
            label='艾宾浩斯复习法', marker='o', markevery=cumulative[1:], 
            markersize=10, markeredgecolor='black', markeredgewidth=2)
    
    # 标记复习点
    colors = ['#FF6B6B', '#FFA07A', '#FFD93D', '#6BCF7F', '#4ECDC4', '#95E1D3']
    for i, review_day in enumerate(cumulative[1:]):
        if review_day < len(memory_with_review):
            ax.axvline(x=review_day, color=colors[i], linestyle=':', alpha=0.5)
            ax.text(review_day, 105, f'L{i}复习',
                   ha='center', fontsize=9, rotation=0,
                   bbox=dict(boxstyle='round', facecolor=colors[i], alpha=0.3))
    
    # 填充区域
    ax.fill_between(days, no_review, memory_with_review, 
                    where=[m > n for m, n in zip(memory_with_review, no_review)],
                    alpha=0.2, color='green', label='复习带来的收益')
    
    ax.set_xlabel('学习天数', fontsize=14, fontweight='bold')
    ax.set_ylabel('记忆保持率 (%)', fontsize=14, fontweight='bold')
    ax.set_title('艾宾浩斯复习法 vs 自然遗忘对比', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, cumulative[-1] + 5)
    ax.set_ylim(0, 110)
    ax.grid(alpha=0.3, linestyle='--')
    ax.legend(fontsize=12, loc='upper right')
    
    # 添加说明文本
    ax.text(cumulative[-1] // 2, 15, 
           '通过科学复习，30天后仍可保持80%以上的记忆',
           ha='center', fontsize=11, style='italic',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    plt.tight_layout()
    
    # 保存图片
    output_path = os.path.join(os.path.dirname(__file__), 'memory_retention.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 记忆保持率对比图已保存: {output_path}")
    
    return output_path


def plot_study_example():
    """绘制实际学习案例"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 模拟30天的学习数据
    days = list(range(1, 31))
    
    # 每日新词 (稳定在5个)
    new_words = [5] * 30
    
    # 复习词逐渐增加
    review_words = []
    for d in days:
        if d <= 1:
            review = 0
        elif d <= 3:
            review = 5
        elif d <= 7:
            review = 10
        elif d <= 15:
            review = 15
        else:
            review = 20
        review_words.append(review)
    
    # 总词数
    total_words = [n + r for n, r in zip(new_words, review_words)]
    
    # 绘制堆叠条形图
    ax.bar(days, new_words, label='新词', color='#FF6B6B', alpha=0.8)
    ax.bar(days, review_words, bottom=new_words, label='复习词', color='#4ECDC4', alpha=0.8)
    
    # 绘制总数曲线
    ax.plot(days, total_words, 'o-', color='#2F3542', linewidth=2, 
           label='每日总数', markersize=6, markeredgecolor='white')
    
    ax.set_xlabel('学习天数', fontsize=14, fontweight='bold')
    ax.set_ylabel('单词数量', fontsize=14, fontweight='bold')
    ax.set_title('30天学习负荷变化 (每天5个新词)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, 31)
    ax.set_ylim(0, 30)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.legend(fontsize=12, loc='upper left')
    
    # 添加阶段标注
    ax.axvspan(1, 3, alpha=0.1, color='green', label='适应期')
    ax.axvspan(4, 15, alpha=0.1, color='yellow')
    ax.axvspan(16, 30, alpha=0.1, color='orange')
    
    ax.text(2, 27, '适应期\n负荷较轻', ha='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='green', alpha=0.3))
    ax.text(10, 27, '积累期\n复习增多', ha='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    ax.text(23, 27, '稳定期\n持续复习', ha='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))
    
    plt.tight_layout()
    
    # 保存图片
    output_path = os.path.join(os.path.dirname(__file__), 'study_load.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 学习负荷图已保存: {output_path}")
    
    return output_path


def main():
    """生成所有可视化图表"""
    print("=" * 60)
    print("艾宾浩斯算法可视化")
    print("=" * 60)
    print()
    
    try:
        print("正在生成图表...")
        print()
        
        # 生成三张图
        plot_review_intervals()
        plot_mastery_progression()
        plot_study_example()
        
        print()
        print("=" * 60)
        print("✓ 所有图表生成完成！")
        print("=" * 60)
        print()
        print("生成的图表:")
        print("  1. ebbinghaus_curve.png - 复习间隔和时间轴")
        print("  2. memory_retention.png - 记忆保持率对比")
        print("  3. study_load.png - 30天学习负荷变化")
        print()
        
    except ImportError as e:
        print(f"✗ 缺少依赖库: {e}")
        print("请安装 matplotlib: pip install matplotlib")
        return 1
    except Exception as e:
        print(f"✗ 生成图表失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
