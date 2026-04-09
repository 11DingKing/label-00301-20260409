"""
API 测试
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.papers.models import Paper
from apps.exams.models import Exam
from apps.grading.models import GradingTask


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='testadmin',
        email='testadmin@example.com',
        password='testpass123',
        role='admin'
    )


@pytest.fixture
def teacher_user(db):
    return User.objects.create_user(
        username='testteacher',
        email='testteacher@example.com',
        password='testpass123',
        role='teacher'
    )


@pytest.fixture
def student_user(db):
    return User.objects.create_user(
        username='teststudent',
        email='teststudent@example.com',
        password='testpass123',
        role='student'
    )


@pytest.fixture
def authenticated_client(api_client, teacher_user):
    """返回已认证的客户端"""
    api_client.force_authenticate(user=teacher_user)
    return api_client


@pytest.fixture
def paper(db, teacher_user):
    """测试用试卷"""
    return Paper.objects.create(
        title='测试试卷',
        description='这是一份测试试卷',
        total_score=100,
        pass_score=60,
        time_limit=60,
        status=Paper.Status.PUBLISHED,
        created_by=teacher_user
    )


@pytest.fixture
def exam(db, paper, teacher_user):
    """测试用考试"""
    now = timezone.now()
    return Exam.objects.create(
        title='测试考试',
        description='这是一份测试考试',
        paper=paper,
        type=Exam.Type.EXAM,
        status=Exam.Status.ENDED,
        start_time=now - timezone.timedelta(hours=2),
        end_time=now - timezone.timedelta(hours=1),
        created_by=teacher_user
    )


@pytest.fixture
def grading_task(db, exam, teacher_user):
    """测试用阅卷任务"""
    return GradingTask.objects.create(
        exam=exam,
        grader=teacher_user,
        status=GradingTask.Status.PENDING,
        total_count=10,
        graded_count=0
    )


class TestAuthAPI:
    """认证 API 测试"""

    def test_login_success(self, api_client, teacher_user):
        """测试登录成功"""
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testteacher',
            'password': 'testpass123'
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'tokens' in response.data['data']
        assert 'access' in response.data['data']['tokens']
        assert 'refresh' in response.data['data']['tokens']

    def test_login_wrong_password(self, api_client, teacher_user):
        """测试密码错误"""
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testteacher',
            'password': 'wrongpassword'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_success(self, api_client, db):
        """测试注册成功"""
        response = api_client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert User.objects.filter(username='newuser').exists()


class TestQuestionsAPI:
    """题目 API 测试"""

    def test_list_questions(self, authenticated_client):
        """测试获取题目列表"""
        response = authenticated_client.get('/api/v1/questions/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'results' in response.data['data']

    def test_create_question(self, authenticated_client):
        """测试创建题目"""
        data = {
            'title': '测试题目',
            'type': 'single',
            'difficulty': 1,
            'score': 5,
            'content': '这是一道测试题',
            'answer': 'A',
            'options': [
                {'label': 'A', 'content': '选项A', 'is_correct': True},
                {'label': 'B', 'content': '选项B', 'is_correct': False},
            ],
            'is_public': True
        }
        response = authenticated_client.post('/api/v1/questions/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_unauthorized_access(self, api_client):
        """测试未认证访问"""
        response = api_client.get('/api/v1/questions/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPapersAPI:
    """试卷 API 测试"""

    def test_list_papers(self, authenticated_client):
        """测试获取试卷列表"""
        response = authenticated_client.get('/api/v1/papers/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True

    def test_create_paper(self, authenticated_client):
        """测试创建试卷"""
        data = {
            'title': '测试试卷',
            'description': '这是一份测试试卷',
            'total_score': 100,
            'pass_score': 60,
            'time_limit': 60
        }
        response = authenticated_client.post('/api/v1/papers/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


class TestTagsAPI:
    """标签 API 测试"""

    def test_list_tags(self, authenticated_client):
        """测试获取标签列表"""
        response = authenticated_client.get('/api/v1/tags/tags/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_categories(self, authenticated_client):
        """测试获取分类列表"""
        response = authenticated_client.get('/api/v1/tags/categories/')
        assert response.status_code == status.HTTP_200_OK


class TestExamsAPI:
    """考试 API 测试"""

    def test_list_exams(self, authenticated_client):
        """测试获取考试列表"""
        response = authenticated_client.get('/api/v1/exams/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True


class TestGradingTaskModel:
    """阅卷任务模型测试"""

    def test_create_grading_task(self, db, grading_task):
        """测试创建阅卷任务"""
        assert grading_task.status == GradingTask.Status.PENDING
        assert grading_task.total_count == 10
        assert grading_task.graded_count == 0
        assert GradingTask.objects.filter(id=grading_task.id).exists()

    def test_default_status(self, db, exam, teacher_user):
        """测试默认状态为 pending"""
        task = GradingTask.objects.create(
            exam=exam,
            grader=teacher_user,
            total_count=10,
            graded_count=0
        )
        assert task.status == GradingTask.Status.PENDING

    def test_str_method(self, db, grading_task):
        """测试 __str__ 方法"""
        expected_str = f'{grading_task.exam.title} - {grading_task.grader.username}'
        assert str(grading_task) == expected_str


class TestGradingTaskStatusFlow:
    """阅卷任务状态流转测试"""

    def test_pending_to_in_progress(self, db, grading_task):
        """测试状态从 pending 流转到 in_progress"""
        assert grading_task.status == GradingTask.Status.PENDING
        
        grading_task.status = GradingTask.Status.IN_PROGRESS
        grading_task.assigned_at = timezone.now()
        grading_task.save()
        
        grading_task.refresh_from_db()
        assert grading_task.status == GradingTask.Status.IN_PROGRESS
        assert grading_task.assigned_at is not None

    def test_in_progress_to_completed(self, db, grading_task):
        """测试状态从 in_progress 流转到 completed"""
        grading_task.status = GradingTask.Status.IN_PROGRESS
        grading_task.assigned_at = timezone.now()
        grading_task.save()
        
        grading_task.status = GradingTask.Status.COMPLETED
        grading_task.completed_at = timezone.now()
        grading_task.graded_count = grading_task.total_count
        grading_task.save()
        
        grading_task.refresh_from_db()
        assert grading_task.status == GradingTask.Status.COMPLETED
        assert grading_task.completed_at is not None
        assert grading_task.graded_count == grading_task.total_count

    def test_full_status_flow(self, db, exam, teacher_user):
        """测试完整的状态流转：pending → in_progress → completed"""
        task = GradingTask.objects.create(
            exam=exam,
            grader=teacher_user,
            status=GradingTask.Status.PENDING,
            total_count=5,
            graded_count=0
        )
        
        assert task.status == GradingTask.Status.PENDING
        assert task.progress == 0
        
        task.status = GradingTask.Status.IN_PROGRESS
        task.assigned_at = timezone.now()
        task.graded_count = 2
        task.save()
        
        task.refresh_from_db()
        assert task.status == GradingTask.Status.IN_PROGRESS
        assert task.progress == 40.0
        
        task.status = GradingTask.Status.COMPLETED
        task.completed_at = timezone.now()
        task.graded_count = 5
        task.save()
        
        task.refresh_from_db()
        assert task.status == GradingTask.Status.COMPLETED
        assert task.progress == 100.0
        assert task.completed_at is not None

    def test_status_choices(self):
        """测试状态选项是否正确"""
        expected_choices = [
            ('pending', '待分配'),
            ('in_progress', '进行中'),
            ('completed', '已完成'),
            ('reviewed', '已复核'),
        ]
        assert GradingTask.Status.choices == expected_choices


class TestGradingTaskProgress:
    """阅卷任务进度测试"""

    def test_progress_with_total_count_zero(self, db, exam, teacher_user):
        """测试 progress 属性在 total_count 为 0 时不报除零错误"""
        task = GradingTask.objects.create(
            exam=exam,
            grader=teacher_user,
            status=GradingTask.Status.PENDING,
            total_count=0,
            graded_count=0
        )
        
        try:
            progress = task.progress
            assert progress == 0, f"Expected progress to be 0, got {progress}"
        except ZeroDivisionError:
            pytest.fail("progress 属性在 total_count 为 0 时抛出了 ZeroDivisionError")

    def test_progress_with_total_count_zero_and_graded_count_nonzero(self, db, exam, teacher_user):
        """测试 total_count 为 0 但 graded_count 不为 0 的情况"""
        task = GradingTask.objects.create(
            exam=exam,
            grader=teacher_user,
            status=GradingTask.Status.IN_PROGRESS,
            total_count=0,
            graded_count=5
        )
        
        assert task.progress == 0

    def test_progress_calculation(self, db, exam, teacher_user):
        """测试进度计算是否正确"""
        task = GradingTask.objects.create(
            exam=exam,
            grader=teacher_user,
            status=GradingTask.Status.IN_PROGRESS,
            total_count=10,
            graded_count=3
        )
        
        assert task.progress == 30.0
        
        task.graded_count = 5
        task.save()
        task.refresh_from_db()
        assert task.progress == 50.0
        
        task.graded_count = 10
        task.save()
        task.refresh_from_db()
        assert task.progress == 100.0

    def test_progress_rounding(self, db, exam, teacher_user):
        """测试进度计算的四舍五入"""
        task = GradingTask.objects.create(
            exam=exam,
            grader=teacher_user,
            status=GradingTask.Status.IN_PROGRESS,
            total_count=3,
            graded_count=1
        )
        
        assert task.progress == 33.33
        
        task.graded_count = 2
        task.save()
        task.refresh_from_db()
        assert task.progress == 66.67

    def test_progress_when_graded_count_exceeds_total_count(self, db, exam, teacher_user):
        """测试 graded_count 超过 total_count 的情况"""
        task = GradingTask.objects.create(
            exam=exam,
            grader=teacher_user,
            status=GradingTask.Status.IN_PROGRESS,
            total_count=10,
            graded_count=15
        )
        
        assert task.progress == 150.0
