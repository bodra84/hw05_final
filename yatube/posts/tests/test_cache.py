from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Pupkin')

    def setUp(self):
        self.authorized_user = Client()

    def test_cache_index_page(self):
        """Проверяем кэширование на Главной странице."""
        page = reverse('posts:index')
        test_post = Post.objects.create(author=self.user, text='Пост номер 1')
        response_1 = self.authorized_user.get(page)
        test_post.delete()
        response_2 = self.authorized_user.get(page)
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_user.get(page)
        self.assertNotEqual(response_1.content, response_3.content)
