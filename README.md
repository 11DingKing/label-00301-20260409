# 在线考试系统 (Online Exam System)

企业级在线考试与刷题系统，支持多种题型、自动阅卷、成绩统计等功能。

## How to Run

### 环境要求

- Docker >= 20.10
- Docker Compose >= 2.0

### 一键启动（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd 301

# 2. 启动所有服务（包含自动初始化）
docker-compose up --build -d

# 3. 等待服务启动完成（约 30-60 秒），查看状态
docker-compose ps

# 4. 初始化测试数据（创建测试账号）
docker-compose exec backend python manage.py shell -c "
from apps.accounts.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin')
if not User.objects.filter(username='teacher').exists():
    User.objects.create_user('teacher', 'teacher@example.com', 'teacher123', role='teacher')
if not User.objects.filter(username='student').exists():
    User.objects.create_user('student', 'student@example.com', 'student123', role='student')
print('测试账号创建成功!')
"

# 5. 验证服务
curl http://localhost:8000/api/docs/
```

### 停止服务

```bash
# 停止服务
docker-compose down

# 停止并删除数据卷（清除所有数据）
docker-compose down -v
```

### 本地开发

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Services

| 服务 | 端口 | 说明 |
|------|------|------|
| Backend API | http://localhost:8000 | Django 后端 API |
| API 文档 (Swagger) | http://localhost:8000/api/docs/ | API 接口文档 |
| API 文档 (ReDoc) | http://localhost:8000/api/redoc/ | API 接口文档 |
| Admin 后台 | http://localhost:8000/admin/ | Django 管理后台 |
| PostgreSQL | localhost:5432 | 数据库 |
| Redis | localhost:6379 | 缓存/消息队列 |

---

## 测试账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 系统管理员，拥有所有权限 |
| 教师 | teacher | teacher123 | 可创建题目、试卷、考试 |
| 学生 | student | student123 | 可参加考试、查看成绩 |

---

## 题目内容

### API 测试命令 (curl)

以下是供质检人员使用的完整测试命令，请按顺序执行：

#### 1. 健康检查

```bash
# 检查 API 文档是否可访问
curl -s http://localhost:8000/api/docs/ | head -20

# 检查 API Schema
curl -s http://localhost:8000/api/schema/ | head -5
```

#### 2. 用户认证测试

```bash
# ===== 2.1 用户注册 =====
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'

# 期望结果: {"success":true,"message":"注册成功",...}

# ===== 2.2 用户登录（教师账号）=====
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher","password":"teacher123"}'

# 期望结果: {"success":true,"message":"登录成功","data":{"user":{...},"tokens":{"access":"...","refresh":"..."}}}

# ===== 2.3 保存 Token（后续测试需要）=====
# Linux/Mac:
export TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher","password":"teacher123"}' | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['data']['tokens']['access'])")

echo "Token: $TOKEN"

# ===== 2.4 获取当前用户信息 =====
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer $TOKEN"

# 期望结果: 返回当前登录用户的详细信息
```

#### 3. 题目管理测试

```bash
# ===== 3.1 获取题目列表 =====
curl -X GET "http://localhost:8000/api/v1/questions/" \
  -H "Authorization: Bearer $TOKEN"

# 期望结果: {"success":true,"data":{"count":0,"results":[],...}}

# ===== 3.2 创建单选题 =====
curl -X POST http://localhost:8000/api/v1/questions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python 中哪个关键字用于定义函数？",
    "type": "single",
    "difficulty": 1,
    "score": 5,
    "content": "以下哪个关键字在 Python 中用于定义函数？",
    "answer": "A",
    "answer_analysis": "def 是 Python 中用于定义函数的关键字",
    "options": [
      {"label": "A", "content": "def", "is_correct": true},
      {"label": "B", "content": "function", "is_correct": false},
      {"label": "C", "content": "func", "is_correct": false},
      {"label": "D", "content": "define", "is_correct": false}
    ],
    "is_public": true
  }'

# 期望结果: 返回创建的题目详情

# ===== 3.3 创建多选题 =====
curl -X POST http://localhost:8000/api/v1/questions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "以下哪些是 Python 的内置数据类型？",
    "type": "multi",
    "difficulty": 2,
    "score": 10,
    "content": "请选择所有正确的答案",
    "answer": "A,B,C",
    "answer_analysis": "list、dict、tuple 都是 Python 内置数据类型",
    "options": [
      {"label": "A", "content": "list", "is_correct": true},
      {"label": "B", "content": "dict", "is_correct": true},
      {"label": "C", "content": "tuple", "is_correct": true},
      {"label": "D", "content": "array", "is_correct": false}
    ],
    "is_public": true
  }'

# ===== 3.4 创建判断题 =====
curl -X POST http://localhost:8000/api/v1/questions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python 是一种编译型语言",
    "type": "judge",
    "difficulty": 1,
    "score": 5,
    "content": "判断：Python 是一种编译型语言",
    "answer": "False",
    "answer_analysis": "Python 是解释型语言，不是编译型语言",
    "is_public": true
  }'

# ===== 3.5 再次获取题目列表（验证创建成功）=====
curl -X GET "http://localhost:8000/api/v1/questions/" \
  -H "Authorization: Bearer $TOKEN"

# 期望结果: count 应该为 3

# ===== 3.6 获取题目详情 =====
curl -X GET "http://localhost:8000/api/v1/questions/1/" \
  -H "Authorization: Bearer $TOKEN"

# ===== 3.7 题目统计 =====
curl -X GET "http://localhost:8000/api/v1/questions/statistics/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. 试卷管理测试

```bash
# ===== 4.1 获取试卷列表 =====
curl -X GET "http://localhost:8000/api/v1/papers/" \
  -H "Authorization: Bearer $TOKEN"

# ===== 4.2 创建试卷 =====
curl -X POST http://localhost:8000/api/v1/papers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python 基础测试",
    "description": "Python 基础知识测试，包含选择题和判断题",
    "total_score": 100,
    "pass_score": 60,
    "time_limit": 60
  }'

# ===== 4.3 获取试卷详情 =====
curl -X GET "http://localhost:8000/api/v1/papers/1/" \
  -H "Authorization: Bearer $TOKEN"

# ===== 4.4 向试卷添加题目 =====
curl -X POST "http://localhost:8000/api/v1/papers/1/add_questions/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question_ids": [1, 2, 3]
  }'
```

#### 5. 标签与分类测试

```bash
# ===== 5.1 获取标签列表 =====
curl -X GET "http://localhost:8000/api/v1/tags/tags/" \
  -H "Authorization: Bearer $TOKEN"

# ===== 5.2 创建标签 =====
curl -X POST "http://localhost:8000/api/v1/tags/tags/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Python", "color": "#3776ab"}'

# ===== 5.3 获取分类列表 =====
curl -X GET "http://localhost:8000/api/v1/tags/categories/" \
  -H "Authorization: Bearer $TOKEN"

# ===== 5.4 创建分类 =====
curl -X POST "http://localhost:8000/api/v1/tags/categories/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "编程语言", "description": "各种编程语言相关题目"}'
```

#### 6. 考试管理测试

```bash
# ===== 6.1 获取考试列表 =====
curl -X GET "http://localhost:8000/api/v1/exams/" \
  -H "Authorization: Bearer $TOKEN"

# ===== 6.2 创建考试 =====
curl -X POST http://localhost:8000/api/v1/exams/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python 入门考试",
    "description": "Python 基础知识入门考试",
    "paper": 1,
    "start_time": "2026-01-27T10:00:00Z",
    "end_time": "2026-12-31T23:59:59Z",
    "duration": 60,
    "is_public": true
  }'
```

#### 7. 权限测试

```bash
# ===== 7.1 未认证访问（应返回 401）=====
curl -X GET "http://localhost:8000/api/v1/questions/"

# 期望结果: {"detail":"Authentication credentials were not provided."}

# ===== 7.2 学生账号登录 =====
export STUDENT_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}' | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['data']['tokens']['access'])")

# ===== 7.3 学生尝试创建题目（应返回 403）=====
curl -X POST http://localhost:8000/api/v1/questions/ \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "test", "type": "single", "difficulty": 1, "score": 5}'

# 期望结果: 403 Forbidden（学生无权创建题目）
```

#### 8. 完整测试脚本

```bash
#!/bin/bash
# 保存为 test_api.sh 并执行: chmod +x test_api.sh && ./test_api.sh

echo "========== 在线考试系统 API 测试 =========="
BASE_URL="http://localhost:8000"

# 1. 健康检查
echo -e "\n[1] 健康检查..."
curl -s "$BASE_URL/api/docs/" > /dev/null && echo "✅ API 文档可访问" || echo "❌ API 文档不可访问"

# 2. 登录获取 Token
echo -e "\n[2] 用户登录..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher","password":"teacher123"}')

TOKEN=$(echo $RESPONSE | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',{}).get('tokens',{}).get('access',''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
  echo "✅ 登录成功"
else
  echo "❌ 登录失败: $RESPONSE"
  exit 1
fi

# 3. 获取题目列表
echo -e "\n[3] 获取题目列表..."
RESPONSE=$(curl -s "$BASE_URL/api/v1/questions/" -H "Authorization: Bearer $TOKEN")
echo $RESPONSE | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'✅ 题目数量: {d[\"data\"][\"count\"]}')" 2>/dev/null || echo "❌ 失败"

# 4. 创建题目
echo -e "\n[4] 创建题目..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/questions/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试题目",
    "type": "single",
    "difficulty": 1,
    "score": 5,
    "content": "这是一道测试题",
    "answer": "A",
    "options": [
      {"label": "A", "content": "正确", "is_correct": true},
      {"label": "B", "content": "错误", "is_correct": false}
    ],
    "is_public": true
  }')
echo $RESPONSE | grep -q '"title"' && echo "✅ 题目创建成功" || echo "❌ 题目创建失败"

# 5. 获取试卷列表
echo -e "\n[5] 获取试卷列表..."
RESPONSE=$(curl -s "$BASE_URL/api/v1/papers/" -H "Authorization: Bearer $TOKEN")
echo $RESPONSE | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'✅ 试卷数量: {d[\"data\"][\"count\"]}')" 2>/dev/null || echo "❌ 失败"

# 6. 获取考试列表
echo -e "\n[6] 获取考试列表..."
RESPONSE=$(curl -s "$BASE_URL/api/v1/exams/" -H "Authorization: Bearer $TOKEN")
echo $RESPONSE | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'✅ 考试数量: {d[\"data\"][\"count\"]}')" 2>/dev/null || echo "❌ 失败"

# 7. 权限测试
echo -e "\n[7] 权限测试（未认证访问）..."
RESPONSE=$(curl -s "$BASE_URL/api/v1/questions/")
echo $RESPONSE | grep -q "credentials were not provided" && echo "✅ 权限验证正常" || echo "❌ 权限验证异常"

echo -e "\n========== 测试完成 =========="
```

---

### 核心功能

1. **用户管理** - 支持学生、教师、管理员三种角色
2. **题库管理** - 支持单选、多选、判断、填空、简答、编程等题型
3. **试卷管理** - 支持组卷、大题小题结构、随机排序
4. **考试管理** - 支持定时考试、限时答题、防作弊
5. **答题提交** - 支持实时保存、自动提交
6. **阅卷功能** - 客观题自动判分、主观题人工阅卷
7. **成绩统计** - 分数统计、排名、题目分析

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django 4.x + Django REST Framework |
| 认证方式 | JWT (SimpleJWT) |
| 数据库 | PostgreSQL |
| 缓存 | Redis |
| 异步任务 | Celery |
| API 文档 | drf-spectacular (Swagger) |
| 容器化 | Docker + Docker Compose |

---

## 项目结构

```
301/
├── docker-compose.yml          # Docker 编排文件
├── .gitignore                  # Git 忽略规则
├── README.md                   # 项目说明（本文件）
└── backend/                    # 后端项目
    ├── Dockerfile              # 后端 Docker 构建文件
    ├── README.md               # 后端说明文档
    ├── requirements.txt        # Python 依赖
    ├── manage.py               # Django 管理脚本
    ├── pytest.ini              # 测试配置
    ├── tests/                  # 测试用例
    ├── config/                 # 项目配置
    ├── apps/                   # 业务模块
    │   ├── accounts/           # 用户系统
    │   ├── questions/          # 题库
    │   ├── exams/              # 考试
    │   ├── papers/             # 试卷
    │   ├── submissions/        # 答题记录
    │   ├── grading/            # 阅卷
    │   ├── statistics/         # 统计
    │   ├── tags/               # 标签
    │   └── commons/            # 公共组件
    └── utils/                  # 工具类
```

## 子项目文档

- [后端文档 (Backend)](./backend/README.md)

## 运行测试

```bash
# Docker 环境中运行测试
docker-compose exec backend pytest tests/ -v

# 本地运行测试
cd backend
source venv/bin/activate
pytest tests/ -v
```

## License

MIT License
