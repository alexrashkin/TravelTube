import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём автора поста
        cls.user = User.objects.create(username='TestAuthor')
        # Создаём запись в БД для тестовой группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание',
        )
        # Создаём запись в БД для проверки редактирования поста
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем клиент автора поста
        self.author_client = Client()
        self.author_client.force_login(self.user)

        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def test_post_create(self):
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif',
        )
        # Готовим данные для заполнения полей формы
        form_data = {
            'text': 'Тестовая запись',
            'group': self.group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.author_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile', kwargs={
                             'username': self.post.author.username}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post_object = Post.objects.first()
        # Проверяем, что создалась запись с заданным слагом
        self.assertEqual(post_object.text, form_data['text'])
        self.assertEqual(post_object.group.id, form_data['group'])
        post_object = Post.objects.first()
        self.assertEqual(post_object.image.name,
                         'posts/' + form_data.get('image').name)

    def test_edit_post(self):
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=self.small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Редактированный текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.author_client.post(
            reverse(
                'posts:edit_post', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True)
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        # Проверяем, что количество постов не увеличилось
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что запись была отредактирована
        post_object = Post.objects.get(id=self.post.pk)
        self.assertEqual(post_object.group.id, form_data['group'])
        self.assertEqual(post_object.text, form_data['text'])
        self.assertEqual(post_object.image.name,
                         'posts/' + form_data.get('image').name)
