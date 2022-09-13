from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель создает таблицу с описанием группы поста."""
    title = models.CharField(max_length=200, verbose_name="Группа")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Путь")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        """Класс задает удобочитаемое имя."""
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель создает таблицу поста с его наименованием и содержанием."""
    text = models.TextField(verbose_name='Пост')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts', verbose_name='Автор')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='posts', verbose_name='Группа')
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """Класс описывает порядок сортировки и задает удобочитаемое имя."""
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:settings.OUTPUT_ELEMENTS_OF_POSTS]


class Comment(models.Model):
    """Модель создает таблицу комментарий к посту."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments', verbose_name='Автор')
    text = models.TextField(verbose_name='Комментарий')
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        """Класс описывает порядок сортировки и задает удобочитаемое имя."""
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    """Модель создает таблицу подписки пользователя на авторов."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               blank=True, null=True,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        """Класс описывает порядок сортировки и задает удобочитаемое имя."""
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
