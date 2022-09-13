from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    """Тестируем доступность страниц и проверку шаблонов приложения Posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='Pupkin')
        cls.user2 = User.objects.create_user(username='Pechkin')
        cls.guest = Client()
        Group.objects.create(
            title='Собаки',
            slug='dogs',
            description='Блог о собаках',
        )
        cls.post = Post.objects.create(
            author=cls.user1,
            text='У меня есть прекрасный пес по кличке Барбоскин',
        )

    def setUp(self):
        self.authorized_user1 = Client()
        self.authorized_user2 = Client()
        self.authorized_user1.force_login(self.user1)
        self.authorized_user2.force_login(self.user2)
        self.template_url_names = {
            '/unexisting_page/': '',
            '/': 'posts/index.html',
            '/group/dogs/': 'posts/group_list.html',
            '/profile/Pupkin/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        self.user_guest = {'user': self.guest,
                           'pages': 5,
                           }
        self.user2 = {'user': self.authorized_user2,
                      'pages': 6,
                      }
        self.user1 = {'user': self.authorized_user1,
                      'pages': 7,
                      }
        self.url_names = list(self.template_url_names.keys())

    def url_exists(self, user, pages):
        """Функция проверяет доступность URL адресов для пользователя user"""
        for i in range(pages):
            address = self.url_names[i]
            with self.subTest(address=address):
                response = user.get(address)
                if address != '/unexisting_page/':
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)

    def test_posts_url_exists_at_desired_location_for_user_guest(self):
        """Проверка доступности URL адресов для пользователя user_guest."""
        self.url_exists(**self.user_guest)

    def test_posts_url_exists_at_desired_location_for_user2(self):
        """Проверка доступности URL адресов для пользователя user2."""
        self.url_exists(**self.user2)

    def test_posts_url_exists_at_desired_location_for_user1(self):
        """Проверка доступности URL адресов для пользователя user1."""
        self.url_exists(**self.user1)

    def test_posts_urls_uses_correct_template(self):
        """Проверка соответствия html-шаблонов URL адресам приложения Posts."""
        for address, template in self.template_url_names.items():
            if address != '/unexisting_page/':
                with self.subTest(address=address):
                    response = self.authorized_user1.get(address)
                    self.assertTemplateUsed(response, template)
