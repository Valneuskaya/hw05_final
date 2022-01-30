from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_post_model_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post_post = PostModelTest.post
        expected_post_name = post_post.text[:15]
        self.assertEqual(expected_post_name, str(post_post))

    def test_group_model_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        post_group = PostModelTest.group
        expected_group_name = post_group.title
        self.assertEqual(expected_group_name, str(post_group))

    def test_post_verbose_name(self):
        """verbose_name Post в полях совпадает с ожидаемым."""
        post_post = PostModelTest.post
        field_verboses_post = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post_post._meta.get_field(value).verbose_name, expected)

    def test_group_verbose_name(self):
        """verbose_name Group в полях совпадает с ожидаемым."""
        post_group = PostModelTest.group
        field_verboses_group = {
            'title': 'Заголовок',
            'slug': 'Адрес страницы группы',
            'description': 'Описание',
        }
        for value, expected in field_verboses_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post_group._meta.get_field(value).verbose_name, expected)
