from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, User


class CacheTests(TestCase):
    def setUp(self):
        # Создаем неавторизованного пользователя
        self.guest_client = Client()

    def test_cache_index2(self):
        """Проверка кеширования главной страницы index."""
        author = User.objects.create_user(username='Lera')
        Post.objects.create(
            text='test_text',
            pub_date='test_date',
            author=author,
        )
        response1 = self.guest_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response2 = self.guest_client.get(reverse('posts:index'))
        # Проверяем, что клиент все еще отдает пост (из кэша)
        self.assertEqual(response1.content, response2.content)
        # Очищаем кэш
        cache.clear()
        # Проверяем, что клиент больше не отдает пост
        response3 = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response2.content, response3.content)
