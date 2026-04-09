"""
答题记录模型
"""
from django.db import models

from utils.mixins import TimeStampMixin


class Answer(TimeStampMixin, models.Model):
    """
    答题记录模型
    记录用户对每道题的作答
    """

    class Status(models.TextChoices):
        NOT_ANSWERED = 'not_answered', '未作答'
        ANSWERED = 'answered', '已作答'
        MARKED = 'marked', '已标记'
        GRADED = 'graded', '已批改'

    # 关联
    submission = models.ForeignKey(
        'submissions.Submission',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='提交记录'
    )
    paper_question = models.ForeignKey(
        'papers.PaperQuestion',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='试卷题目'
    )

    # 作答内容
    answer_content = models.TextField('作答内容', blank=True, help_text='选择题存选项ID，其他题存文本')
    answer_files = models.JSONField('作答附件', default=list, blank=True, help_text='编程题代码文件等')

    # 状态
    status = models.CharField(
        '状态',
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_ANSWERED
    )
    is_marked = models.BooleanField('是否标记', default=False)

    # 评分
    score = models.DecimalField('得分', max_digits=5, decimal_places=1, null=True, blank=True)
    is_correct = models.BooleanField('是否正确', null=True, blank=True)

    # 批改
    comment = models.TextField('批改评语', blank=True)
    graded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_answers',
        verbose_name='批改人'
    )
    graded_at = models.DateTimeField('批改时间', null=True, blank=True)

    # 时间记录
    first_answer_time = models.DateTimeField('首次作答时间', null=True, blank=True)
    last_answer_time = models.DateTimeField('最后作答时间', null=True, blank=True)
    answer_duration = models.PositiveIntegerField('作答时长(秒)', default=0)

    class Meta:
        db_table = 'answers'
        verbose_name = '答题记录'
        verbose_name_plural = verbose_name
        unique_together = [['submission', 'paper_question']]
        ordering = ['submission', 'paper_question__question_number']

    def __str__(self):
        return f'{self.submission.user.username} - 第{self.paper_question.question_number}题'

    @property
    def question(self):
        """关联的题目"""
        return self.paper_question.question

    @property
    def max_score(self):
        """满分"""
        return self.paper_question.score

    def auto_grade(self):
        """
        自动批改（客观题）
        返回是否成功批改
        """
        question = self.question

        # 只有客观题才能自动批改
        if not question.is_objective:
            return False

        correct_answer = question.answer
        user_answer = self.answer_content

        if question.type == 'single':
            # 单选题：直接比较
            self.is_correct = user_answer == correct_answer
            self.score = self.max_score if self.is_correct else 0

        elif question.type == 'multi':
            # 多选题：比较集合
            correct_set = set(correct_answer.split(','))
            user_set = set(user_answer.split(',')) if user_answer else set()

            if user_set == correct_set:
                self.is_correct = True
                self.score = self.max_score
            elif user_set.issubset(correct_set) and user_set:
                # 部分正确，给一半分
                self.is_correct = False
                self.score = self.max_score / 2
            else:
                self.is_correct = False
                self.score = 0

        elif question.type == 'judge':
            # 判断题：比较
            self.is_correct = user_answer.lower() == correct_answer.lower()
            self.score = self.max_score if self.is_correct else 0

        self.status = self.Status.GRADED
        self.save()

        return True
