from http import HTTPStatus

from django.test import TestCase


class CoreTestClass(TestCase):
    def test_error_page(self):
        """Тест, что статус ответа сервера - 404"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_uses_correct_template(self):
        """Тест: URL-адрес использует соответствующий шаблон."""
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
