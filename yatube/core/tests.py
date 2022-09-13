from http import HTTPStatus

from django.test import Client, TestCase


class ViewTestClass(TestCase):
    """Тестируем кастомные страницы."""
    def setUp(self):
        self.user = Client()

    def test_error_page(self):
        """Тестируем что страница 404 отдает кастомный шаблон."""
        response = self.user.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
