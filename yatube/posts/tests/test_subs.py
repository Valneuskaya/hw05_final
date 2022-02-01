from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, User, Follow

User = get_user_model()


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='1')
        cls.author = User.objects.create_user(username='2')
        cls.another_user = User.objects.create_user(username='3')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тест',
        )

    def setUp(self):
        # Создаем авторизованного пользователя
        self.authorized_client_follower = Client()
        self.authorized_client_follower.force_login(self.follower)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        self.authorized_client_another_user = Client()
        self.authorized_client_another_user.force_login(self.another_user)

    def test_auth_can_subs(self):
        """Тест, что Авторизованный пользователь может подписываться"""
        # Подписываемся юзером1 на юзера2
        self.authorized_client_follower.post(reverse(
            'posts:profile_follow', kwargs={'username': self.author.username}),
            follow=True
        )
        # Проверяем подписку
        self.assertTrue(Follow.objects.filter(
            user=self.follower, author=self.author).count() > 0)

    def test_auth_can_unsubs(self):
        """Тест, что Авторизованный пользователь может отписываться"""
        # Подписываемся юзером1 на юзера2
        follow_obj = Follow.objects.create(
            user=self.follower,
            author=self.author,
        )
        # Проверяем подписку
        self.assertIn(follow_obj, Follow.objects.filter(
            user=self.follower, author=self.author))
        # Отписываемся юзером1 на юзера2
        self.authorized_client_follower.post(reverse(
            'posts:profile_unfollow', kwargs={
                'username': self.author.username}), follow=True
        )
        # Проверяем отписку
        self.assertNotIn(follow_obj, Follow.objects.filter(
            user=self.follower, author=self.author))

    def test_subs_visible(self):
        """Тест подписки"""
        # Подписываемся
        Follow.objects.create(
            user=self.follower,
            author=self.author,
        )
        # Проверяем список постов
        response = self.authorized_client_follower.get(
            reverse('posts:follow_index'))
        self.assertEqual(1, len(response.context['page_obj']))
        response = self.authorized_client_another_user.get(
            reverse('posts:follow_index'))
        self.assertEqual(0, len(response.context['page_obj']))
