from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    """Тестируем доступность страниц и проверку шаблонов приложения About."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()
        cls.template_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности URL адресов приложения About."""
        for address in self.template_url_names.values():
            with self.subTest(address=address):
                response = self.guest.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_uses_correct_template(self):
        """Проверка соответствия html-шаблонов URL адресам приложения About."""
        for template, address in self.template_url_names.items():
            with self.subTest(address=address):
                response = self.guest.get(address)
                self.assertTemplateUsed(response, template)
