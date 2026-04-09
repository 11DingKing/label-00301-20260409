#!/usr/bin/env python
"""
初始化数据脚本
创建测试账号和示例数据
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
django.setup()

from apps.accounts.models import User
from apps.questions.models import Question, Option
from apps.tags.models import Tag, Category
from apps.papers.models import Paper


def create_users():
    """创建测试用户"""
    print("创建测试用户...")
    
    # 管理员
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        print("  ✅ 管理员账号创建成功: admin / admin123")
    else:
        print("  ⏭️ 管理员账号已存在")
    
    # 教师
    if not User.objects.filter(username='teacher').exists():
        User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='teacher123',
            role='teacher'
        )
        print("  ✅ 教师账号创建成功: teacher / teacher123")
    else:
        print("  ⏭️ 教师账号已存在")
    
    # 学生
    if not User.objects.filter(username='student').exists():
        User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123',
            role='student'
        )
        print("  ✅ 学生账号创建成功: student / student123")
    else:
        print("  ⏭️ 学生账号已存在")


def create_categories_and_tags():
    """创建分类和标签"""
    print("\n创建分类和标签...")
    
    # 创建分类
    categories_data = [
        {'name': '编程语言', 'description': '各种编程语言相关题目'},
        {'name': '数据结构', 'description': '数据结构与算法相关题目'},
        {'name': '数据库', 'description': '数据库相关题目'},
    ]
    
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"  ✅ 分类创建成功: {cat.name}")
    
    # 创建标签
    tags_data = [
        {'name': 'Python', 'color': '#3776ab'},
        {'name': 'Java', 'color': '#007396'},
        {'name': 'JavaScript', 'color': '#f7df1e'},
        {'name': '基础', 'color': '#28a745'},
        {'name': '进阶', 'color': '#fd7e14'},
    ]
    
    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_data['name'],
            defaults={'color': tag_data['color']}
        )
        if created:
            print(f"  ✅ 标签创建成功: {tag.name}")


def create_sample_questions():
    """创建示例题目"""
    print("\n创建示例题目...")
    
    teacher = User.objects.filter(role='teacher').first()
    if not teacher:
        print("  ❌ 未找到教师账号，跳过题目创建")
        return
    
    category = Category.objects.filter(name='编程语言').first()
    python_tag = Tag.objects.filter(name='Python').first()
    basic_tag = Tag.objects.filter(name='基础').first()
    
    questions_data = [
        {
            'title': 'Python 中哪个关键字用于定义函数？',
            'type': 'single',
            'difficulty': 1,
            'score': 5,
            'content': '以下哪个关键字在 Python 中用于定义函数？',
            'answer': 'A',
            'answer_analysis': 'def 是 Python 中用于定义函数的关键字',
            'options': [
                {'label': 'A', 'content': 'def', 'is_correct': True},
                {'label': 'B', 'content': 'function', 'is_correct': False},
                {'label': 'C', 'content': 'func', 'is_correct': False},
                {'label': 'D', 'content': 'define', 'is_correct': False},
            ]
        },
        {
            'title': '以下哪些是 Python 的内置数据类型？',
            'type': 'multi',
            'difficulty': 2,
            'score': 10,
            'content': '请选择所有正确的答案',
            'answer': 'A,B,C',
            'answer_analysis': 'list、dict、tuple 都是 Python 内置数据类型，array 需要导入 numpy',
            'options': [
                {'label': 'A', 'content': 'list', 'is_correct': True},
                {'label': 'B', 'content': 'dict', 'is_correct': True},
                {'label': 'C', 'content': 'tuple', 'is_correct': True},
                {'label': 'D', 'content': 'array', 'is_correct': False},
            ]
        },
        {
            'title': 'Python 是一种编译型语言',
            'type': 'judge',
            'difficulty': 1,
            'score': 5,
            'content': '判断：Python 是一种编译型语言',
            'answer': 'False',
            'answer_analysis': 'Python 是解释型语言，不是编译型语言',
            'options': []
        },
        {
            'title': 'Python 中用于输出的函数是什么？',
            'type': 'blank',
            'difficulty': 1,
            'score': 5,
            'content': 'Python 中用于输出的内置函数是 ____',
            'answer': 'print',
            'answer_analysis': 'print() 是 Python 中用于输出的内置函数',
            'options': []
        },
        {
            'title': '请简述 Python 中 list 和 tuple 的区别',
            'type': 'short',
            'difficulty': 2,
            'score': 15,
            'content': '请简述 Python 中 list 和 tuple 的主要区别',
            'answer': 'list 是可变的，tuple 是不可变的',
            'answer_analysis': '主要区别：1. list 可变，tuple 不可变；2. list 用方括号，tuple 用圆括号；3. tuple 的性能更好',
            'options': []
        },
    ]
    
    for q_data in questions_data:
        if Question.objects.filter(title=q_data['title']).exists():
            print(f"  ⏭️ 题目已存在: {q_data['title'][:20]}...")
            continue
        
        options_data = q_data.pop('options')
        question = Question.objects.create(
            created_by=teacher,
            category=category,
            is_public=True,
            **q_data
        )
        
        # 创建选项
        for opt_data in options_data:
            Option.objects.create(question=question, **opt_data)
        
        # 添加标签
        if python_tag:
            question.tags.add(python_tag)
        if basic_tag:
            question.tags.add(basic_tag)
        
        print(f"  ✅ 题目创建成功: {q_data['title'][:30]}...")


def create_sample_paper():
    """创建示例试卷"""
    print("\n创建示例试卷...")
    
    teacher = User.objects.filter(role='teacher').first()
    if not teacher:
        print("  ❌ 未找到教师账号，跳过试卷创建")
        return
    
    if Paper.objects.filter(title='Python 基础测试').exists():
        print("  ⏭️ 试卷已存在")
        return
    
    paper = Paper.objects.create(
        title='Python 基础测试',
        description='Python 基础知识测试，包含选择题、判断题、填空题和简答题',
        total_score=40,
        pass_score=24,
        time_limit=30,
        created_by=teacher,
        status='published',
        is_random_question=False,
        is_random_option=True,
    )
    
    # 将所有题目添加到试卷
    from apps.papers.models import PaperQuestion
    questions = Question.objects.all()
    for idx, question in enumerate(questions):
        PaperQuestion.objects.create(
            paper=paper,
            question=question,
            order=idx + 1,
            score=question.score
        )
    
    print(f"  ✅ 试卷创建成功: {paper.title}")


def main():
    """主函数"""
    print("=" * 50)
    print("初始化数据开始")
    print("=" * 50)
    
    create_users()
    create_categories_and_tags()
    create_sample_questions()
    create_sample_paper()
    
    print("\n" + "=" * 50)
    print("初始化数据完成!")
    print("=" * 50)
    print("\n测试账号:")
    print("  - 管理员: admin / admin123")
    print("  - 教师: teacher / teacher123")
    print("  - 学生: student / student123")
    print("\nAPI 文档: http://localhost:8000/api/docs/")
    print("管理后台: http://localhost:8000/admin/")


if __name__ == '__main__':
    main()
