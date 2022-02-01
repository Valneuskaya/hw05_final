from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Заголовок',
        max_length=200,
        help_text='Введите заголовок поста'
    )
    slug = models.SlugField(
        'Адрес страницы группы',
        unique=True
    )
    description = models.TextField(
        'Описание',
        help_text='Введите описание группы'
    )

    class Meta:
        verbose_name = 'Group'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='group_posts',
        blank=True, null=True,
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    # Поле для картинки (необязательное)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    # Аргумент upload_to указывает директорию,
    # в которую будут загружаться пользовательские файлы.

    class Meta:
        verbose_name = 'Post'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
        blank=False,
        null=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментатор'
    )
    text = models.TextField(
        max_length=20000,
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
        blank=False
    )

    class Meta:
        verbose_name = 'Comment'
        ordering = ['pub_date']

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписывающийся'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписант'
    )

    class Meta:
        verbose_name = 'Follow'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='user_author'
            ),
            models.CheckConstraint(
                name='author_author',
                check=~models.Q(user=models.F('author'))
            )
        ]
