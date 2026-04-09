"""
搜索服务
支持 PostgreSQL 全文检索和可选的 Elasticsearch 集成
"""
from django.conf import settings
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity,
)
from django.db.models import Q, Value, F
from django.db.models.functions import Greatest


class SearchService:
    """
    搜索服务类
    提供全文检索功能，支持 PostgreSQL 和 Elasticsearch
    """

    def __init__(self):
        self.use_elasticsearch = getattr(settings, 'USE_ELASTICSEARCH', False)
        if self.use_elasticsearch:
            self._init_elasticsearch()

    def _init_elasticsearch(self):
        """初始化 Elasticsearch 客户端"""
        try:
            from elasticsearch import Elasticsearch
            self.es_client = Elasticsearch(
                hosts=getattr(settings, 'ELASTICSEARCH_HOSTS', ['http://localhost:9200']),
                http_auth=(
                    getattr(settings, 'ELASTICSEARCH_USERNAME', ''),
                    getattr(settings, 'ELASTICSEARCH_PASSWORD', '')
                ) if getattr(settings, 'ELASTICSEARCH_USERNAME', '') else None
            )
        except ImportError:
            self.use_elasticsearch = False
            self.es_client = None

    def search_questions(self, query, queryset=None, limit=50):
        """
        搜索题目
        
        Args:
            query: 搜索关键词
            queryset: 基础查询集（可选）
            limit: 返回结果数量限制
            
        Returns:
            搜索结果 QuerySet 或列表
        """
        if self.use_elasticsearch and self.es_client:
            return self._search_with_elasticsearch(query, queryset, limit)
        return self._search_with_postgres(query, queryset, limit)

    def _search_with_postgres(self, query, queryset=None, limit=50):
        """
        使用 PostgreSQL 全文检索
        """
        from apps.questions.models import Question

        if queryset is None:
            queryset = Question.objects.filter(is_deleted=False)

        if not query:
            return queryset[:limit]

        # 构建搜索向量
        # weight: A > B > C > D，权重从高到低
        search_vector = (
            SearchVector('title', weight='A', config='simple') +
            SearchVector('content', weight='B', config='simple') +
            SearchVector('answer', weight='C', config='simple') +
            SearchVector('answer_analysis', weight='D', config='simple')
        )

        # 构建搜索查询
        search_query = SearchQuery(query, config='simple')

        # 计算搜索排名
        search_rank = SearchRank(search_vector, search_query)

        # 三元组相似度（用于模糊匹配）
        title_similarity = TrigramSimilarity('title', query)
        content_similarity = TrigramSimilarity('content', query)

        # 综合相似度
        combined_similarity = Greatest(title_similarity, content_similarity)

        # 执行搜索
        results = queryset.annotate(
            search=search_vector,
            rank=search_rank,
            similarity=combined_similarity,
        ).filter(
            Q(search=search_query) |
            Q(similarity__gt=0.1) |
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).order_by('-rank', '-similarity')[:limit]

        return results

    def _search_with_elasticsearch(self, query, queryset=None, limit=50):
        """
        使用 Elasticsearch 搜索
        """
        from apps.questions.models import Question

        if not query:
            if queryset is None:
                return Question.objects.filter(is_deleted=False)[:limit]
            return queryset[:limit]

        # Elasticsearch 查询
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content^2", "answer", "answer_analysis"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            },
            "size": limit
        }

        try:
            response = self.es_client.search(
                index=getattr(settings, 'ELASTICSEARCH_QUESTION_INDEX', 'questions'),
                body=body
            )

            # 提取 ID 并保持顺序
            ids = [hit['_id'] for hit in response['hits']['hits']]

            if not ids:
                return Question.objects.none()

            # 从数据库获取完整对象
            id_ordering = {id: idx for idx, id in enumerate(ids)}
            questions = Question.objects.filter(id__in=ids, is_deleted=False)

            # 按 ES 返回的相关性排序
            return sorted(questions, key=lambda q: id_ordering.get(str(q.id), 999))

        except Exception as e:
            # ES 搜索失败，降级到 PostgreSQL
            return self._search_with_postgres(query, queryset, limit)

    def index_question(self, question):
        """
        将题目索引到 Elasticsearch
        """
        if not self.use_elasticsearch or not self.es_client:
            return

        doc = {
            'title': question.title,
            'content': question.content,
            'answer': question.answer,
            'answer_analysis': question.answer_analysis,
            'type': question.type,
            'difficulty': question.difficulty,
            'category_id': question.category_id,
            'tags': list(question.tags.values_list('name', flat=True)),
            'created_at': question.created_at.isoformat() if question.created_at else None,
        }

        try:
            self.es_client.index(
                index=getattr(settings, 'ELASTICSEARCH_QUESTION_INDEX', 'questions'),
                id=str(question.id),
                body=doc
            )
        except Exception as e:
            pass  # 静默失败，不影响主流程

    def delete_question_index(self, question_id):
        """
        从 Elasticsearch 删除题目索引
        """
        if not self.use_elasticsearch or not self.es_client:
            return

        try:
            self.es_client.delete(
                index=getattr(settings, 'ELASTICSEARCH_QUESTION_INDEX', 'questions'),
                id=str(question_id)
            )
        except Exception:
            pass

    def bulk_index_questions(self, questions):
        """
        批量索引题目到 Elasticsearch
        """
        if not self.use_elasticsearch or not self.es_client:
            return

        from elasticsearch.helpers import bulk

        actions = []
        for question in questions:
            actions.append({
                '_index': getattr(settings, 'ELASTICSEARCH_QUESTION_INDEX', 'questions'),
                '_id': str(question.id),
                '_source': {
                    'title': question.title,
                    'content': question.content,
                    'answer': question.answer,
                    'answer_analysis': question.answer_analysis,
                    'type': question.type,
                    'difficulty': question.difficulty,
                    'category_id': question.category_id,
                    'tags': list(question.tags.values_list('name', flat=True)),
                    'created_at': question.created_at.isoformat() if question.created_at else None,
                }
            })

        try:
            bulk(self.es_client, actions)
        except Exception:
            pass


# 全局搜索服务实例
search_service = SearchService()
