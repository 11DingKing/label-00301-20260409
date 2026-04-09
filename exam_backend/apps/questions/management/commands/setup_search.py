"""
设置 PostgreSQL 全文检索扩展
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = '设置 PostgreSQL 全文检索扩展（pg_trgm）和搜索索引'

    def add_arguments(self, parser):
        parser.add_argument(
            '--index-only',
            action='store_true',
            help='仅创建索引，不安装扩展',
        )

    def handle(self, *args, **options):
        self.stdout.write('开始设置 PostgreSQL 全文检索...')

        with connection.cursor() as cursor:
            # 检查是否是 PostgreSQL
            if connection.vendor != 'postgresql':
                self.stdout.write(
                    self.style.WARNING('当前数据库不是 PostgreSQL，全文检索功能将使用 ILIKE 降级方案')
                )
                return

            if not options['index_only']:
                # 安装 pg_trgm 扩展（用于三元组相似度搜索）
                self.stdout.write('安装 pg_trgm 扩展...')
                try:
                    cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
                    self.stdout.write(self.style.SUCCESS('pg_trgm 扩展安装成功'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'pg_trgm 扩展安装失败: {e}'))

                # 安装 unaccent 扩展（用于忽略重音符号）
                self.stdout.write('安装 unaccent 扩展...')
                try:
                    cursor.execute('CREATE EXTENSION IF NOT EXISTS unaccent;')
                    self.stdout.write(self.style.SUCCESS('unaccent 扩展安装成功'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'unaccent 扩展安装失败: {e}'))

            # 创建 GIN 索引用于全文搜索
            self.stdout.write('创建全文搜索索引...')
            try:
                # 题目表的全文搜索索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS questions_search_idx 
                    ON questions 
                    USING GIN (to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(content, '')));
                ''')
                self.stdout.write(self.style.SUCCESS('全文搜索索引创建成功'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'全文搜索索引创建失败: {e}'))

            # 创建三元组索引用于模糊搜索
            self.stdout.write('创建三元组模糊搜索索引...')
            try:
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS questions_title_trgm_idx 
                    ON questions 
                    USING GIN (title gin_trgm_ops);
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS questions_content_trgm_idx 
                    ON questions 
                    USING GIN (content gin_trgm_ops);
                ''')
                self.stdout.write(self.style.SUCCESS('三元组索引创建成功'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'三元组索引创建失败: {e}'))

        self.stdout.write(self.style.SUCCESS('PostgreSQL 全文检索设置完成！'))
        self.stdout.write('')
        self.stdout.write('使用方法:')
        self.stdout.write('  GET /api/v1/questions/?q=搜索关键词')
        self.stdout.write('  GET /api/v1/questions/?search=搜索关键词')
