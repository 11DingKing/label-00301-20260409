"""
API 测试
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User


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
