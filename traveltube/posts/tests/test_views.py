from django import forms
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём автора поста
        cls.user = User.objects.create_user(username='TestAuthor')
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
        cls.follower = User.objects.create_user(username='Follow')
        cls.no_follower = User.objects.create_user(username='No_Follow')
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.user
        )

    def setUp(self):
        # Создаём клиенты
        self.author_client = Client()
        self.authorized_client = Client()
        self.follower_client = Client()
        self.no_follower_client = Client()
        self.no_follower_client.force_login(self.no_follower)
        self.follower_client.force_login(self.follower)
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(self.user)

        # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        # Проверяем использование соответствующего шаблона URL-адресом
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={
                    'username': self.post.author.username}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}): (
                'posts/post_detail.html'
            ),
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:edit_post', kwargs={'post_id': self.post.pk}): (
                'posts/create_post.html'
            ),
        }
        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    """ Проверяем словарь контекста страницы /post_create, в котором
    передаётся форма
    """
    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        """ Проверяем, что типы полей формы в словаре context соответствуют
        ожиданиям
        """
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    """ Проверяем, что словарь context главной страницы в первом элементе
    списка page_obj содержит ожидаемые значения
    """
    def test_index_show_correct_context(self):
        # Проверяем, что шаблон index сформирован с правильным контекстом
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_group_title_0 = first_object.group.title
        post_group_slug_0 = first_object.group.slug
        post_group_description_0 = first_object.group.description
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_group_title_0, self.group.title)
        self.assertEqual(post_group_slug_0, self.group.slug)
        self.assertEqual(post_group_description_0, self.group.description)

    def test_create_post_with_group_on_main_page(self):
        # Проверяем отображение поста с группой на главной странице
        response = self.authorized_client.get(reverse('posts:index'))
        count = len(response.context['page_obj'])
        Post.objects.create(
            text='Тестовый пост_2',
            author=self.user,
            group=self.group,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        count_2 = len(response.context['page_obj'])
        self.assertEqual(count + 1, count_2)

    def test_create_post_with_group_on_group_page(self):
        # Проверяем отображение поста с группой на странице выбранной группы
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug}))
        count = len(response.context['page_obj'])
        Post.objects.create(
            text='Тестовый пост_3',
            author=self.user,
            group=self.group,
        )
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug}))
        count_2 = len(response.context['page_obj'])
        self.assertEqual(count + 1, count_2)

    def test_create_post_with_group_on_profile_page(self):
        # Проверяем отображение поста с группой в профайле пользователя
        response = self.author_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author.username}))
        count = len(response.context['page_obj'])
        Post.objects.create(
            text='Тестовый пост_4',
            author=self.user,
            group=self.group,
        )
        response = self.author_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author.username}))
        count_2 = len(response.context['page_obj'])
        self.assertEqual(count + 1, count_2)

    def test_image_on_main_page(self):
        # Проверяем отображение картинки на главной странице
        image_on_page = {
            reverse('posts:index')
        }
        for page in image_on_page:
            with self.subTest(page=page):
                response = self.client.get(page)
                obj = response.context["page_obj"][0]
                self.assertEqual(obj.image, self.post.image)

    def test_image_on_profile_page(self):
        # Проверяем отображение картинки на странице профайла
        image_on_page = {
            reverse('posts:profile', kwargs={
                    'username': self.post.author.username})
        }
        for page in image_on_page:
            with self.subTest(page=page):
                response = self.client.get(page)
                obj = response.context["page_obj"][0]
                self.assertEqual(obj.image, self.post.image)

    def test_image_on_group_page(self):
        # Проверяем отображение картинки на странице группы
        response = self.author_client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug}))
        obj = response.context["page_obj"][0]
        self.assertEqual(obj.image, self.post.image)

    def test_image_on_post_detail_page(self):
        # Проверяем отображение картинки на отдельной странице поста
        response = self.author_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        obj = response.context["post"]
        self.assertEqual(obj.image, self.post.image)

    def test_comment_on_post_detail_page(self):
        # Проверяем отображение поста с группой на странице выбранной группы
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        count = len(response.context['comments'])
        Comment.objects.create(
            text='Тестовый комментарий',
            author=self.user,
            post=self.post,
        )
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        count_2 = len(response.context['comments'])
        self.assertEqual(count + 1, count_2)

    def test_check_cache(self):
        # Проверяем работу кеша
        response1 = self.authorized_client.get(reverse("posts:index"))
        Post.objects.all().delete()
        response2 = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.authorized_client.get(reverse("posts:index"))
        self.assertNotEqual(response1.content, response3.content)

    def test_amount_of_posts(self):
        # Проверяем, что посты у подписчиков добавляются
        response = self.follower_client.get(reverse("posts:follow_index"))
        count_follower = len(response.context["page_obj"])
        response = self.no_follower_client.get(reverse("posts:follow_index"))
        count_no_follower = len(response.context["page_obj"])
        Post.objects.create(
            text='new post for follower',
            author=self.user
        )
        response = self.follower_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), count_follower + 1)
        response = self.no_follower_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), count_no_follower)

    def test_following(self):
        # Проверяем, что можно подписаться
        response_follow = self.no_follower_client.get(reverse(
            "posts:follow_index"))
        self.assertEqual(response_follow.context.get(
            "page_obj").paginator.count, 0)
        response_follow = self.no_follower_client.get(reverse(
            "posts:profile_follow", kwargs={'username': self.user}))
        response_follow = self.no_follower_client.get(reverse(
            "posts:follow_index"))
        self.assertEqual(response_follow.context.get(
            "page_obj").paginator.count, 1)

    def test_unfollowing(self):
        # Проверяем, что можно отписаться
        response_follow = self.follower_client.get(reverse(
            "posts:follow_index"))
        self.assertEqual(response_follow.context.get(
            "page_obj").paginator.count, 1)
        response_follow = self.follower_client.get(reverse(
            "posts:profile_unfollow", kwargs={'username': self.user}))
        response_follow = self.follower_client.get(reverse(
            "posts:follow_index"))
        self.assertEqual(response_follow.context.get(
            "page_obj").paginator.count, 0)

    def test_no_self_follow(self):
        # Проверяем невозможность подписаться на самого себя
        self.authorized_client.get(reverse(
            "posts:profile_follow", kwargs={'username': self.user}))
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.user).exists())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём автора поста
        cls.user = User.objects.create(username='TestAuthor2')
        # Создаём запись в БД для тестовой группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание',
        )
        # Создаём 13 тестовых записей
        Post.objects.bulk_create(
            [
                Post(author=cls.user, text=f'Текст поста{i}',
                     group=cls.group)
                for i in range(13)
            ]
        )

    def setUp(self):
        # Создаём клиент автора поста
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_limited_number_of_posts(self):
        # Проверяем работу paginator (список постов)
        posts_on_page = {
            reverse('posts:index'): 10,
            (reverse('posts:index') + '?page=2'): 3,
        }
        for page, num_of_posts in posts_on_page.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']),
                                 num_of_posts
                                 )

    def test_limited_number_of_posts(self):
        # Проверяем работу paginator(список постов: фильтр по группе)
        posts_on_page = {
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}): 10,
            (reverse('posts:group_posts', kwargs={'slug': self.group.slug})
             + '?page=2'): 3,
        }
        for page, num_of_posts in posts_on_page.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']),
                                 num_of_posts
                                 )

    def test_limited_number_of_posts(self):
        # Проверяем работу paginator(список постов: фильтр по пользователю)
        posts_on_page = {
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): 10,
            (reverse('posts:profile',
                     kwargs={'username': self.user.username}) + '?page=2'): 3,
        }
        for page, num_of_posts in posts_on_page.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']),
                                 num_of_posts
                                 )
