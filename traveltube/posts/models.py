from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from PIL import Image as PilImage

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Тема')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста')
    image = models.ImageField(
        verbose_name='Аватар поста',
        upload_to='posts/',
        blank=False,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    images = models.ManyToManyField(
        'Image',
        through='PostImage'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Image(models.Model):
    Image = models.ImageField(upload_to='images/')

    def clean(self):
        super().clean()
        img = PilImage.open(self.image)
        if img.format not in ('JPEG', 'WEBP', 'PNG'):
            raise ValidationError(
                'Недопустимый формат файла. '
                'Поддерживаются только JPEG, WEBP и PNG.'
            )


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        img = PilImage.open(self.image)
        if img.format not in ('JPEG', 'WEBP', 'PNG'):
            raise ValidationError(
                'Недопустимый формат файла. '
                'Поддерживаются только JPEG, WEBP и PNG.'
            )


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Комментарий'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='unique_subscription')]
