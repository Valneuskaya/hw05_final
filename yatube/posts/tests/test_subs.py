from itertools import count
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, User, Follow

User = get_user_model()


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='1')
        cls.user_2 = User.objects.create_user(username='2')
        cls.user_3 = User.objects.create_user(username='3')
        cls.post = Post.objects.create(
            author=cls.user_1,
            text='Тест',
        )

    def setUp(self):
        # Создаем неавторизованного пользователя
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(self.user_3)

    def test_auth_can_subs(self):
        """Тест, что Авторизованный пользователь может подписываться"""
        # Подписываемся юзером1 на юзера2
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': self.user_2.username}),
            follow=True
        )
        # Проверяем подписку
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user_2.username})
        )
        self.assertTrue(response.context['following'])

    def test_auth_can_unsubs(self):
        """Тест, что Авторизованный пользователь может отписываться"""
        # Подписываемся юзером1 на юзера2
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': self.user_2.username}),
            follow=True
        )
        # Проверяем подписку
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user_2.username})
        )
        self.assertTrue(response.context['following'])
        # Отписываемся юзером1 на юзера2
        self.authorized_client.post(reverse(
            'posts:profile_unfollow', kwargs={'username': self.user_2.username}),
            follow=True
        )
        # Проверяем отписку
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user_2.username})
        )
        self.assertFalse(response.context['following'])

    def test_subs_visible(self):
        """Тест подписки"""
        # Подписываемся юзером2 на юзера1
        self.authorized_client_2.post(reverse(
            'posts:profile_follow', kwargs={'username': self.user_1.username}),
            follow=True
        )
        # Проверяем подписку
        response = self.authorized_client_2.get(reverse(
            'posts:profile', kwargs={'username': self.user_1.username})
        )
        self.assertTrue(response.context['following'])
        response = self.authorized_client_3.get(reverse(
            'posts:profile', kwargs={'username': self.user_1.username})
        )
        self.assertFalse(response.context['following'])
        # Проверяем список постов
        response = self.authorized_client_2.get(reverse('posts:follow_index'))
        self.assertEqual(1, len(response.context['page_obj']))
        response = self.authorized_client_3.get(reverse('posts:follow_index'))
        self.assertEqual(0, len(response.context['page_obj']))
