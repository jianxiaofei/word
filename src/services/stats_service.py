# -*- coding: utf-8 -*-
"""统计业务服务"""

from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
from core.database import DatabaseManager


class StatsService:
    """统计相关业务逻辑"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_user_stats(self, user_id: int) -> Dict:
        """获取用户统计数据"""
        words = self.db.get_user_bound_words(user_id)
        today = datetime.now().date().isoformat()
        
        total = len(words)
        # status=1 表示学习中
        total_learned = sum(1 for w in words if w.get('status') == 1)
        # 掌握度>=5的认为已掌握
        mastered = sum(1 for w in words if w.get('mastery_level', 0) >= 5)
        # 计算总复习次数
        total_reviews = sum(w.get('review_count', 0) for w in words)
        # 今日待复习：next_review == today 且 status=1
        today_review_count = sum(1 for w in words if w.get('next_review') == today and w.get('status') == 1)
        # 掌握率
        mastery_rate = round(mastered / total * 100, 1) if total > 0 else 0
        # 学习进度
        progress = round(total_learned / total * 100, 1) if total > 0 else 0
        
        # 按掌握程度分布统计
        mastery_distribution = defaultdict(int)
        for word in words:
            level = word.get('mastery_level', 0)
            mastery_distribution[level] += 1
        
        # 最近学习的单词
        recent_words = sorted(
            [w for w in words if w.get('last_review')],
            key=lambda x: x.get('last_review', ''),
            reverse=True
        )[:10]
        
        # 连续学习天数（简化版：暂时返回0）
        streak_days = 0
        
        # 30天学习趋势（简化版：生成空数据）
        daily_stats = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).date().isoformat()
            daily_stats.append({'date': date, 'count': 0})
        
        return {
            'scope': 'user',
            'total': total,
            'total_learned': total_learned,
            'total_reviews': total_reviews,
            'mastery_rate': mastery_rate,
            'progress': progress,
            'streak_days': streak_days,
            'today_review_count': today_review_count,
            'mastery_distribution': dict(mastery_distribution),
            'recent_words': recent_words,
            'daily_stats': daily_stats,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_learning_progress(self, user_id: int, days: int = 30) -> Dict:
        """获取学习进度（最近N天）- 简化版"""
        # 暂时返回空数据，因为数据库没有学习记录表
        result = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
            result.append({
                'date': date,
                'learned': 0,
                'reviewed': 0
            })
        
        return {
            'daily_stats': result,
            'total_days': days
        }
    
    def get_word_distribution(self, user_id: int) -> Dict:
        """获取单词分布统计"""
        words = self.db.get_user_bound_words(user_id)
        
        # 按词库统计
        book_stats = defaultdict(int)
        for word in words:
            book_name = word.get('book_name', 'Unknown')
            book_stats[book_name] += 1
        
        # 按状态统计
        status_stats = defaultdict(int)
        for word in words:
            status = word.get('status', 'unknown')
            status_stats[status] += 1
        
        return {
            'by_book': dict(book_stats),
            'by_status': dict(status_stats)
        }
    
    def get_difficult_words_analysis(self, limit: int = 50) -> Dict:
        """
        获取易错单词分析
        
        Args:
            limit: 返回的易错单词数量限制
            
        Returns:
            包含易错单词列表和统计信息的字典
        """
        # 获取易错单词列表
        difficult_words = self.db.words.get_difficult_words(limit=limit, min_unknown_count=2)
        
        # 获取统计信息
        stats = self.db.words.get_mistake_statistics()
        
        # 为每个单词添加建议
        for word in difficult_words:
            unknown_count = word.get('unknown_count', 0)
            consecutive_correct = word.get('consecutive_correct', 0)
            
            if unknown_count >= 5:
                word['difficulty_level'] = '困难'
                word['suggestion'] = '需要重点复习，建议每天复习'
            elif unknown_count >= 3:
                word['difficulty_level'] = '中等'
                word['suggestion'] = '需要加强记忆，增加复习频率'
            else:
                word['difficulty_level'] = '一般'
                word['suggestion'] = '继续保持复习'
            
            # 计算记忆稳定性（连续正确次数/总错误次数）
            if unknown_count > 0:
                word['stability_score'] = round(consecutive_correct / unknown_count, 2)
            else:
                word['stability_score'] = 1.0
        
        return {
            'difficult_words': difficult_words,
            'statistics': stats,
            'total_count': len(difficult_words),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_learning_efficiency_report(self) -> Dict:
        """
        生成学习效率报告
        
        Returns:
            包含学习效率分析的报告
        """
        stats = self.db.words.get_mistake_statistics()
        difficult_words = self.db.words.get_difficult_words(limit=10, min_unknown_count=3)
        
        # 计算学习效率指标
        total_mistakes = stats['total_mistakes']
        words_with_mistakes = stats['words_with_mistakes']
        avg_mistakes = stats['avg_mistakes']
        
        # 效率评级
        if avg_mistakes < 2:
            efficiency_rating = '优秀'
            efficiency_comment = '学习效率很高，继续保持！'
        elif avg_mistakes < 3:
            efficiency_rating = '良好'
            efficiency_comment = '学习效率不错，可以适当增加学习量'
        elif avg_mistakes < 4:
            efficiency_rating = '一般'
            efficiency_comment = '建议加强复习，特别关注易错单词'
        else:
            efficiency_rating = '需改进'
            efficiency_comment = '建议放慢学习节奏，重点复习已学单词'
        
        return {
            'statistics': stats,
            'efficiency_rating': efficiency_rating,
            'efficiency_comment': efficiency_comment,
            'top_difficult_words': difficult_words[:5],
            'recommendations': [
                '重点复习错误次数≥3的单词',
                '每天复习时优先处理易错单词',
                '可以制作专门的易错单词本',
                '适当降低新词学习速度，确保已学单词掌握牢固'
            ],
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
