# posts/tests/tests_url.py
from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client, созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Lera')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test-description',
        )
        cls.post = Post.objects.create(
            text='test_post_text',
            author=cls.author
        )

    def setUp(self):
        # Создаем неавторизованного пользователя
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.author)

    # Проверяем общедоступные страницы
    def test_urls_posts_template(self):
        """Проверка, что URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.author}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_create_url_exists_at_desired_location(self):
        """Проверка, что создание доступно авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_exists_at_desired_location(self):
        """Проверка, что редакт-е доступно авторизованному пользователю."""
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_create_url_redirect_anonymous(self):
        """Тест о редиректе анонима на домашнюю страницу."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_edit_url_redirect_anonymous(self):
        """Тест о редиректе анонима на страницу просмотра поста."""
        response = self.guest_client.get(
            f'/posts/{PostURLTests.post.id}/edit/')
        self.assertRedirects(
            response,
            (f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/'))

    def test_unexisting_page(self):
        """Тест о несуществующей странице."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
