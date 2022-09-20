from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Follow, Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    """Тестируем доступность страниц и проверку шаблонов приложения Posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='Pupkin')
        cls.user_2 = User.objects.create_user(username='Pechkin')
        cls.guest = Client()
        Group.objects.create(
            title='Собаки',
            slug='dogs',
            description='Блог о собаках',
        )
        cls.post = Post.objects.create(
            author=cls.user_1,
            text='У меня есть прекрасный пес по кличке Барбоскин',
        )
        Follow.objects.create(user=cls.user_2, author=cls.user_1)

    def setUp(self):
        self.authorized_user_1 = Client()
        self.authorized_user_2 = Client()
        self.authorized_user_1.force_login(self.user_1)
        self.authorized_user_2.force_login(self.user_2)
        self.template_url_names = {
            '/unexisting_page/': '',
            '/': 'posts/index.html',
            '/group/dogs/': 'posts/group_list.html',
            f'/profile/{self.user_1}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/comment/': 'posts/post_detail.html',
            '/follow/': 'posts/follow.html',
            f'/profile/{self.user_1}/unfollow/': 'posts/profile.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            f'/profile/{self.user_2}/follow/': 'posts/profile.html',
        }
        self.user_guest = {'user': self.guest,
                           'pages': 5,
                           }
        self.user_2 = {'user': self.authorized_user_2,
                       'pages': 8,
                       }
        self.user_1 = {'user': self.authorized_user_1,
                       'pages': 10,
                       }
        self.url_names = list(self.template_url_names.keys())

    def url_exists(self, user, pages):
        """Функция проверяет доступность URL адресов для пользователя user"""
        for i in range(pages):
            address = self.url_names[i]
            with self.subTest(address=address):
                response = user.get(address, follow=True)
                if address != '/unexisting_page/':
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)

    def test_posts_url_exists_at_desired_location_for_user_guest(self):
        """Проверка доступности URL адресов для пользователя user_guest."""
        self.url_exists(**self.user_guest)

    def test_posts_url_exists_at_desired_location_for_user_2(self):
        """Проверка доступности URL адресов для пользователя user_2."""
        self.url_exists(**self.user_2)

    def test_posts_url_exists_at_desired_location_for_user_1(self):
        """Проверка доступности URL адресов для пользователя user_1."""
        self.url_exists(**self.user_1)

    def test_posts_urls_uses_correct_template(self):
        """Проверка соответствия html-шаблонов URL адресам приложения Posts."""
        for address, template in self.template_url_names.items():
            if address != '/unexisting_page/':
                with self.subTest(address=address):
                    response = self.authorized_user_1.get(address, follow=True)
                    self.assertTemplateUsed(response, template)
