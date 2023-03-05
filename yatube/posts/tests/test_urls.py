from django.test import Client, TestCase

from http import HTTPStatus
from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём авторизованного пользователя
        cls.user = User.objects.create_user(username='TestAuth')
        # Создаём автора поста
        cls.user_author = User.objects.create_user(username='TestAuthor')
        # Создаём запись в БД для тестовой группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание группы'
        )
        # Создаём запись в БД для тестового поста
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user_author,
            group=cls.group,
        )
        cls.status_code_url_names = {
            '/': HTTPStatus.OK,
            f'/group/{cls.group.slug}/': HTTPStatus.OK,
            f'/profile/{cls.post.author.username}/': HTTPStatus.OK,
            f'/posts/{cls.post.pk}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.post.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём клиент для пользователя
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostURLTests.user)
        # Создаём клиент для автора
        self.author_client = Client()
        # Авторизуем автора
        self.author_client.force_login(PostURLTests.user_author)

    # Проверяем доступность страниц для неавторизованного пользователя
    def test_not_auth_url_exists_at_desired_location(self):
        # Проверяем общедоступные страницы
        for address, status_code in self.status_code_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    """"Проверяем редиректы на странице создания поста для неавторизованного
    пользователя.
    """
    def test_post_create_url_redirect_anonymous_on_auth_login(self):
        """Страница /create/ перенаправляет анонимного пользователя
        на страницу авторизации.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )
    """Проверяем редиректы на странице редактирования поста для
    неавторизованного пользователя.
    """
    def test_post_edit_url_redirect_anonymous_on_auth_login(self):
        """Страница /posts/<int:post_id>/edit/ перенаправляет анонимного
        пользователя на страницу авторизации.
        """
        response = self.guest_client.get(f'/posts/{PostURLTests.post.pk}'
                                         '/edit/', follow=True)
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{PostURLTests.post.pk}'
                       '/edit/')
        )

    # Проверяем доступность страницы для авторизованного пользователя
    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Проверка доступности страницы /create/ для авторизованного
        пользователя.
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    """Проверяем редирект на странице редактирования поста для авторизованного
    пользователя (не автора).
    """
    def test_post_edit_url_redirect_authorized_on_post_detail(self):
        """Страница /posts/<int:post_id>/edit/ перенаправляет авторизованного
        пользователя (не автора) на страницу поста.
        """
        response = self.authorized_client.get(f'/posts/{PostURLTests.post.pk}'
                                              '/edit/', follow=True)
        self.assertRedirects(
            response, (f'/posts/{PostURLTests.post.pk}/')
        )

    # Проверяем доступность страницы редактирования поста для автора
    def test_post_edit_url_exists_at_desired_location_authorized(self):
        # Проверка доступности страницы /posts/<int:post_id>/edit/ для автора
        response = self.author_client.get(f'/posts/{PostURLTests.post.pk}'
                                          '/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls(self):
        # Проверка на использование URL-адресов соответствующих шаблонов
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_commenting_by_authorized_user(self):
        # Проверяем, что комментарии может оставлять только авторизованный
        # пользователь
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, (f'/posts/{self.post.pk}/')
        )

    def test_no_authorized_user(self):
        # Проверяем, что неавторизованный пользователь не может оставлять
        # комментарии
        response = self.guest_client.get(f'/posts/{self.post.pk}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.pk}/comment/')
        )


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client, созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
