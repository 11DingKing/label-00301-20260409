# Backend - 在线考试系统后端

基于 Django 4.x + Django REST Framework 构建的企业级在线考试系统后端 API。

## How to Run

### Docker 方式（推荐）

```bash
# 在项目根目录执行
cd ..
docker-compose up --build -d

# 访问 API 文档
open http://localhost:8000/api/docs/
```

### 本地开发

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库等信息

# 4. 数据库迁移
python manage.py migrate

# 5. 创建超级用户
python manage.py createsuperuser

# 6. 启动开发服务器
python manage.py runserver

# 7. 启动 Celery（可选，用于异步任务）
celery -A config worker -l info
celery -A config beat -l info
```

## Services

| 服务         | 地址                             | 说明            |
| ------------ | -------------------------------- | --------------- |
| API 接口     | http://localhost:8000/api/v1/    | RESTful API     |
| Swagger 文档 | http://localhost:8000/api/docs/  | 交互式 API 文档 |
| ReDoc 文档   | http://localhost:8000/api/redoc/ | API 文档        |
| Admin 后台   | http://localhost:8000/admin/     | Django 管理后台 |

## 测试账号

> 通过 Django 管理后台或 API 创建

| 角色   | 用户名  | 密码       | 权限说明                   |
| ------ | ------- | ---------- | -------------------------- |
| 管理员 | admin   | admin123   | 所有权限                   |
| 教师   | teacher | teacher123 | 创建题目、试卷、考试、阅卷 |
| 学生   | student | student123 | 参加考试、查看成绩         |

## 题目内容

### 技术栈

| 技术                  | 版本  | 用途          |
| --------------------- | ----- | ------------- |
| Python                | 3.11+ | 运行环境      |
| Django                | 4.x   | Web 框架      |
| Django REST Framework | 3.14+ | API 框架      |
| SimpleJWT             | 5.3+  | JWT 认证      |
| PostgreSQL            | 15+   | 生产数据库    |
| Redis                 | 7+    | 缓存/消息队列 |
| Celery                | 5.3+  | 异步任务      |
| drf-spectacular       | 0.27+ | API 文档      |
| Gunicorn              | 21+   | WSGI 服务器   |

### 项目结构

```
backend/
├── Dockerfile              # Docker 构建文件
├── .dockerignore           # Docker 忽略文件
├── requirements.txt        # Python 依赖
├── manage.py               # Django 管理脚本
├── .env.example            # 环境变量示例
├── config/                 # 项目配置
│   ├── settings/
│   │   ├── base.py        # 基础配置
│   │   ├── dev.py         # 开发环境
│   │   └── prod.py        # 生产环境
│   ├── urls.py            # URL 路由
│   ├── celery.py          # Celery 配置
│   ├── wsgi.py
│   └── asgi.py
├── apps/                   # 业务模块
│   ├── accounts/          # 用户系统
│   │   ├── models/        # 用户、资料模型
│   │   ├── serializers/   # 序列化器
│   │   ├── views/         # 视图
│   │   └── urls/          # 路由
│   ├── questions/         # 题库系统
│   ├── papers/            # 试卷系统
│   ├── exams/             # 考试系统
│   ├── submissions/       # 答题记录
│   ├── grading/           # 阅卷系统
│   ├── statistics/        # 统计分析
│   ├── tags/              # 标签系统
│   └── commons/           # 公共组件
├── utils/                  # 工具类
│   ├── permissions.py     # 权限类
│   ├── pagination.py      # 分页器
│   ├── mixins.py          # Mixin 类
│   └── exceptions.py      # 异常处理
├── media/                  # 上传文件
├── static/                 # 静态文件
└── logs/                   # 日志文件
```

### 核心模块

| 模块        | 说明                                          |
| ----------- | --------------------------------------------- |
| accounts    | 用户认证（JWT）、角色管理（学生/教师/管理员） |
| questions   | 多题型支持（单选/多选/判断/填空/简答/编程）   |
| papers      | 试卷组卷、大题小题结构                        |
| exams       | 考试规则、时间限制、防作弊                    |
| submissions | 答题记录、实时保存                            |
| grading     | 自动判分（客观题）、人工阅卷（主观题）        |
| statistics  | 成绩统计、排名、错题分析                      |
| tags        | 标签分类管理                                  |
| commons     | 系统配置、操作日志、通知、文件上传            |

### API 接口

#### 认证接口

```
POST   /api/v1/auth/login/           # 登录
POST   /api/v1/auth/register/        # 注册
POST   /api/v1/auth/logout/          # 登出
POST   /api/v1/auth/refresh/         # 刷新 Token
POST   /api/v1/auth/change-password/ # 修改密码
```

#### 用户接口

```
GET    /api/v1/users/                # 用户列表（管理员）
GET    /api/v1/users/me/             # 当前用户信息
PATCH  /api/v1/users/update_me/      # 更新当前用户
GET    /api/v1/users/profile/        # 用户资料
```

#### 题库接口

```
GET    /api/v1/questions/            # 题目列表
POST   /api/v1/questions/            # 创建题目
GET    /api/v1/questions/{id}/       # 题目详情
PUT    /api/v1/questions/{id}/       # 更新题目
DELETE /api/v1/questions/{id}/       # 删除题目
GET    /api/v1/questions/random/     # 随机抽题
GET    /api/v1/questions/statistics/ # 题目统计
```

#### 试卷接口

```
GET    /api/v1/papers/               # 试卷列表
POST   /api/v1/papers/               # 创建试卷
POST   /api/v1/papers/{id}/add_questions/    # 添加题目
POST   /api/v1/papers/{id}/remove_questions/ # 移除题目
POST   /api/v1/papers/{id}/publish/  # 发布试卷
POST   /api/v1/papers/{id}/duplicate/ # 复制试卷
```

#### 考试接口

```
GET    /api/v1/exams/                # 考试列表
POST   /api/v1/exams/                # 创建考试
POST   /api/v1/exams/{id}/start/     # 开始考试
GET    /api/v1/exams/{id}/my_record/ # 我的考试记录
GET    /api/v1/exams/available/      # 可参加的考试
```

#### 答题接口

```
POST   /api/v1/submissions/save_answer/  # 保存答案
POST   /api/v1/submissions/batch_save/   # 批量保存
POST   /api/v1/submissions/submit_exam/  # 提交考试
GET    /api/v1/submissions/get_answers/  # 获取答题记录
GET    /api/v1/submissions/get_result/   # 获取考试结果
```

#### 阅卷接口

```
GET    /api/v1/grading/pending_exams/       # 待阅卷考试
GET    /api/v1/grading/get_answers_to_grade/ # 待批改答案
POST   /api/v1/grading/grade_answer/        # 批改答案
POST   /api/v1/grading/batch_grade/         # 批量批改
```

#### 统计接口

```
GET    /api/v1/statistics/exam/             # 考试统计
GET    /api/v1/statistics/exam_ranking/     # 考试排名
GET    /api/v1/statistics/question_analysis/ # 题目分析
GET    /api/v1/statistics/my_statistics/    # 我的学习统计
GET    /api/v1/statistics/my_weak_points/   # 薄弱知识点
```

### 环境变量

| 变量              | 说明          | 默认值                   |
| ----------------- | ------------- | ------------------------ |
| DEBUG             | 调试模式      | True                     |
| SECRET_KEY        | Django 密钥   | -                        |
| ALLOWED_HOSTS     | 允许的主机    | localhost                |
| DB_NAME           | 数据库名      | exam_db                  |
| DB_USER           | 数据库用户    | -                        |
| DB_PASSWORD       | 数据库密码    | -                        |
| DB_HOST           | 数据库主机    | localhost                |
| DB_PORT           | 数据库端口    | 5432                     |
| REDIS_URL         | Redis 地址    | redis://localhost:6379/0 |
| CELERY_BROKER_URL | Celery Broker | redis://localhost:6379/1 |

## License

MIT License
