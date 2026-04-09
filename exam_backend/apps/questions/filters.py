"""
题目过滤器
支持 PostgreSQL 全文检索
"""
import django_filters
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity,
)
from django.db.models import Q, F

from apps.questions.models import Question


class FullTextSearchFilter(django_filters.CharFilter):
    """
    PostgreSQL 全文检索过滤器
    支持中文分词搜索
    """

    def filter(self, qs, value):
        if not value:
            return qs

        # 创建搜索向量 - 包含标题和内容
        # 使用 'simple' 配置支持中文，或安装 zhparser 扩展后使用 'chinese'
        search_vector = SearchVector('title', weight='A', config='simple') + \
                        SearchVector('content', weight='B', config='simple')

        # 创建搜索查询
        search_query = SearchQuery(value, config='simple')

        # 计算搜索排名
        search_rank = SearchRank(search_vector, search_query)

        # 同时使用三元组相似度进行模糊匹配（需要 pg_trgm 扩展）
        # 这对于短查询词和拼写错误更友好
        title_similarity = TrigramSimilarity('title', value)

        return qs.annotate(
            search=search_vector,
            rank=search_rank,
            title_similarity=title_similarity,
        ).filter(
            Q(search=search_query) | Q(title_similarity__gt=0.1)
        ).order_by('-rank', '-title_similarity')


class QuestionFilter(django_filters.FilterSet):
    """
    题目过滤器
    支持全文检索和标准字段过滤
    """
    # 全文检索字段
    q = FullTextSearchFilter(label='全文搜索')
    search = FullTextSearchFilter(label='搜索')  # 别名

    # 标准过滤字段
    type = django_filters.ChoiceFilter(choices=Question.Type.choices)
    difficulty = django_filters.ChoiceFilter(choices=Question.Difficulty.choices)
    difficulty_min = django_filters.NumberFilter(field_name='difficulty', lookup_expr='gte')
    difficulty_max = django_filters.NumberFilter(field_name='difficulty', lookup_expr='lte')
    score_min = django_filters.NumberFilter(field_name='score', lookup_expr='gte')
    score_max = django_filters.NumberFilter(field_name='score', lookup_expr='lte')
    tag = django_filters.NumberFilter(field_name='tags', lookup_expr='exact')
    tags = django_filters.BaseInFilter(field_name='tags', lookup_expr='in')
    category = django_filters.NumberFilter(field_name='category')
    is_public = django_filters.BooleanFilter()
    created_by = django_filters.NumberFilter(field_name='created_by')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    # 简单模糊搜索（兼容非 PostgreSQL 数据库）
    title_contains = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    content_contains = django_filters.CharFilter(field_name='content', lookup_expr='icontains')

    class Meta:
        model = Question
        fields = [
            'q', 'search', 'type', 'difficulty', 'difficulty_min', 'difficulty_max',
            'score_min', 'score_max', 'tag', 'tags', 'category',
            'is_public', 'created_by', 'created_after', 'created_before',
            'title_contains', 'content_contains'
        ]
