import shutil
import tempfile

from http import HTTPStatus

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, User, Comment


# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоватьсяgs
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Lera')
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            text='test_text',
            pub_date='test_date',
            author=cls.author,
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        # Создаем неавторизованного пользователя
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Тест на создание новой записи в базе данных"""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test_create_post',
            'group': CreateFormTests.group.pk,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={
                'username': self.author.username}))
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверим данные
        created_post = (Post.objects.filter(text=form_data['text'])[0])
        self.assertIsNotNone(created_post)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.author, self.author)
        self.assertEqual(created_post.group, self.group)
        self.assertEqual(created_post.image, 'posts/small.gif')
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_create_post_without_group(self):
        """Тест на создание новой записи в базе данных"""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()
        form_data = {
            'text': 'test_create_post_without_group',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={
                'username': self.author.username}))
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверим данные
        created_post = (Post.objects.filter(text=form_data['text'])[0])
        self.assertIsNotNone(created_post)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.author, self.author)
        self.assertIsNone(created_post.group)
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        """Тест на редактирование записи в базе данных"""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()
        # Проверяем исходный текст
        self.assertEquals('test_text', Post.objects.filter(
            pk=CreateFormTests.post.id)[0].text)
        # Изменяем текст
        form_data = {
            'text': 'test_text edit',
            'group': CreateFormTests.group.pk,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(reverse(
            'posts:post_edit', kwargs={'post_id': CreateFormTests.post.id}),
            data=form_data,
            follow=True
        )
        # Прверяем редирект
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': CreateFormTests.post.id}))
        # Проверяем измененный текст
        CreateFormTests.post.refresh_from_db()
        self.assertEquals(CreateFormTests.post.text, 'test_text edit')
        # Проверяем число постов
        self.assertEqual(Post.objects.count(), post_count)
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, HTTPStatus.OK)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Lera')
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            text='test_text',
            pub_date='test_date',
            author=cls.author,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Текст коммента для теста',
            author=cls.author
        )
        cls.form = CommentForm()
        # Создаем неавторизованного пользователя
        cls.guest_client = Client()
        # Создаем авторизованного пользователя
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.author)

    def test_comment_post(self):
        """Тест на создание нового коммента в базе данных"""
        form_data = {
            'text': 'test_text',
            'post': self.post,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
        )
        # Проверяем редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        # Проверили, что коммент создан
        self.assertTrue(
            Comment.objects.filter(
                text='Текст коммента для теста',
                post=self.post
            ).exists()
        )
