import shutil
import tempfile
from datetime import timedelta
from unittest import mock

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from ..models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    """Тестируем какие шаблоны и контекст используют
    view-функции приложения Posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()
        cls.user = User.objects.create_user(username='Pupkin')
        Group.objects.bulk_create([Group(title='Собаки', slug='dogs',
                                         description='Блог о собаках'),
                                   Group(title='Кошки', slug='cats',
                                         description='Блог о кошках')]
                                  )
        cls.group_dogs = Group.objects.get(title='Собаки')
        cls.group_cats = Group.objects.get(title='Кошки')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(name='small.gif', content=small_gif,
                                          content_type='image/gif')
        cls.post = Post.objects.create(author=cls.user, text='Пост номер 1',
                                       group_id=cls.group_dogs.id,
                                       image=cls.uploaded)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.template_pages_with_page_obj = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group_dogs.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
        }
        self.template_pages_with_post = {
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}): 'posts/post_detail.html',
        }
        self.template_pages_with_form = {
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        self.template_pages_for_group_cats = {
            reverse('posts:group_list', kwargs={
                'slug': self.group_cats.slug}): 'posts/group_list.html',
        }
        self.pages_with_page_obj = list(
            self.template_pages_with_page_obj.keys())
        self.pages_with_post = list(self.template_pages_with_post.keys())
        self.pages_with_form_content = list(
            self.template_pages_with_form.keys())
        self.pages_for_group_cats = list(
            self.template_pages_for_group_cats.keys())

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        all_template_pages = {**self.template_pages_with_page_obj,
                              **self.template_pages_with_post,
                              **self.template_pages_with_form}
        for reverse_name, template in all_template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_index_group_list__profile_page_show_correct_context(self):
        """Шаблоны posts/index.html, posts/group_list.html и posts/profile.html
         сформированы с правильным контекстом."""
        for page in self.pages_with_page_obj:
            response = self.authorized_user.get(page)
            first_object = response.context['page_obj'][0]
            with self.subTest(page=page):
                self.assertEqual(first_object, self.post,
                                 'Пост из запроса не соответствует тестовому!')

    def test_posts_detail_page_show_correct_context(self):
        """Шаблон posts/detail.html сформирован с правильным контекстом."""
        page = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        response = self.authorized_user.get(page)
        post = response.context['post']
        self.assertEqual(post, self.post,
                         'Пост из запроса не соответствует тестовому!')

    def test_posts_create_post_edit_page_show_correct_context(self):
        """Шаблон posts/create.html сформирован с правильным контекстом."""
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField,
                       'image': forms.fields.ImageField,
                       }
        for page in self.pages_with_form_content:
            response = self.authorized_user.get(page)
            for value, expected in form_fields.items():
                with self.subTest(page=page, value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)
                    form_content = response.context.get('form').instance
            with self.subTest(page=page):
                if page == reverse('posts:post_edit',
                                   kwargs={'post_id': self.post.id}):
                    self.assertEqual(form_content.text, self.post.text)
                    self.assertEqual(form_content.group, self.group_dogs)
                    self.assertEqual(form_content.image, self.post.image)
                else:
                    self.assertEqual(form_content.text, '')
                    self.assertIsNone(form_content.group)
                    self.assertEqual(form_content.image, '')

    def test_create_new_post(self):
        """Тестирование отображения нового поста, содержащего группу (group)
        на страницах: Главноя/ страница выбранной группы/ профиля пользователя.
        """
        time_test_now = timezone.now() + timedelta(minutes=1)
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = time_test_now
            test_post = Post.objects.create(author=self.user,
                                            text='Пост номер 2',
                                            group_id=self.group_dogs.id)
        page_names = [*self.pages_with_page_obj, *self.pages_for_group_cats]
        for page in page_names:
            with self.subTest(page=page):
                response = self.authorized_user.get(page)
                if page != reverse('posts:group_list',
                                   kwargs={'slug': self.group_cats.slug}):
                    post = response.context['page_obj'][0]
                    self.assertEqual(post, test_post)
                    self.assertEqual(post.author, test_post.author)
                    self.assertEqual(post.text, test_post.text)
                    self.assertEqual(post.id, test_post.id)
                    self.assertEqual(post.group, test_post.group)
                else:
                    posts = response.context['page_obj']
                    self.assertNotIn(post, posts)

    def test_comment_post_user_guest(self):
        """Тестирование невозможности комментировать пост не авторизированным
        пользователем."""
        page = reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        response = self.guest.get(page, follow=True)
        self.assertRedirects(response, f'/auth/login/?next={page}')

    def test_comment_post_authorized_user(self):
        """Тестирование возможности комментировать пост авторизированным
        пользователем."""
        page = reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        response = self.authorized_user.get(page, follow=True)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id}))


class PaginatorViewsTest(TestCase):
    """Тестируем паджинатор"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Pupkin')
        cls.group_dogs = Group.objects.create(title='Собаки', slug='dogs',
                                              description='Блог о собаках')
        posts = []
        for i in range(1, 14):
            posts.append(Post(author=cls.user, text=f'Пост номер {i}',
                              group_id=cls.group_dogs.id))
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.page_names = [reverse('posts:index'),
                           reverse('posts:group_list',
                                   kwargs={'slug': self.group_dogs.slug}),
                           reverse('posts:profile',
                                   kwargs={'username': self.user})]

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        for page in self.page_names:
            with self.subTest(page=page):
                response = self.authorized_user.get(page)
                count = len(response.context['page_obj'])
                self.assertEqual(count, 10)

    def test_second_page_contains_three_records(self):
        """Проверка: количество постов на второй странице равно 3."""
        for page in self.page_names:
            with self.subTest(page=page + '?page=2'):
                response = self.authorized_user.get(
                    page + '?page=2')
                count = len(response.context['page_obj'])
                self.assertEqual(count, 3)


class FollowingViewsTest(TestCase):
    """Тестируем подписку на автора"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='Пользователь_1')
        cls.user_2 = User.objects.create_user(username='Пользователь_2')
        cls.author_1 = User.objects.create_user(username='author_1')

    def setUp(self):
        self.authorized_user_1 = Client()
        self.authorized_user_1.force_login(self.user_1)
        self.authorized_user_2 = Client()
        self.authorized_user_2.force_login(self.user_2)

    def test_authorized_user_follow(self):
        """Авторизированный пользователь может подписываться на других
        пользователей."""
        page = reverse('posts:profile_follow',
                       kwargs={'username': self.author_1})
        self.authorized_user_1.get(page)
        self.assertTrue(
            Follow.objects.filter(user=self.user_1,
                                  author=self.author_1).exists())

    def test_authorized_user_unfollow(self):
        """Авторизированный пользователь может отписываться от других
        пользователей."""
        Follow.objects.create(user=self.user_2, author=self.author_1)
        page = reverse('posts:profile_unfollow',
                       kwargs={'username': self.author_1})
        self.authorized_user_2.get(page)
        self.assertFalse(
            Follow.objects.filter(user=self.user_2,
                                  author=self.author_1).exists())

    def test_new_post_appears_only_subscriber(self):
        """Новая запись пользователя появляется только у подписчиков"""
        Follow.objects.create(user=self.user_1, author=self.author_1)
        post = Post.objects.create(author=self.author_1,
                                   text='Для подписчиков')
        page = reverse('posts:follow_index')
        response_1 = self.authorized_user_1.get(page)
        response_2 = self.authorized_user_2.get(page)
        test_post_1 = response_1.context['page_obj']
        test_post_2 = response_2.context['page_obj']
        self.assertIn(post, test_post_1)
        self.assertNotIn(post, test_post_2)
