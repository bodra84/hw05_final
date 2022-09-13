import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Тестируем форму приложения Posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Pupkin')
        Group.objects.bulk_create([Group(title='Собаки', slug='dogs',
                                         description='Блог о собаках'),
                                   Group(title='Кошки', slug='cats',
                                         description='Блог о кошках')]
                                  )
        cls.group_dogs = Group.objects.get(title='Собаки')
        cls.group_cats = Group.objects.get(title='Кошки')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(name='small1.gif',
                                          content=cls.small_gif,
                                          content_type='image/gif')
        cls.post = Post.objects.create(author=cls.user, text='Пост номер 1',
                                       group_id=cls.group_dogs.id,
                                       image=cls.uploaded)
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новый пост."""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(name='small2.gif',
                                      content=self.small_gif,
                                      content_type='image/gif')
        form_data = {
            'text': 'Пост номер 2',
            'group': self.group_dogs.id,
            'image': uploaded,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'), data=form_data, follow=True)
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(author=self.user, text='Пост номер 2',
                                group=self.group_dogs.id,
                                image='posts/small2.gif').exists())

    def test_edit_post(self):
        """Валидная форма редактирует существующий пост."""
        post = Post.objects.create(author=self.user, text='Пост номер 3',
                                   group_id=self.group_dogs.id)
        uploaded = SimpleUploadedFile(name='small3.gif',
                                      content=self.small_gif,
                                      content_type='image/gif')
        form_data = {
            'text': 'Пост номер 3 изменен',
            'group': self.group_cats.id,
            'image': uploaded,
        }
        response = self.authorized_user.post(
            reverse('posts:post_edit', args=[post.id]), data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': post.id}))
        post_edit = Post.objects.get(id=post.id)
        self.assertEqual(post_edit.id, post.id)
        self.assertEqual(post_edit.author, self.user)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.group, self.group_cats)
        self.assertEqual(post_edit.image, 'posts/small3.gif')

    def test_create_new_comment(self):
        """Тестирование отображения нового комментария на странице поста."""
        comments_count = Comment.objects.filter(id=self.post.id).count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data, follow=True)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id}))
        self.assertEqual(Comment.objects.filter(id=self.post.id).count(),
                         comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(author=self.user, text=form_data['text'],
                                   post=self.post).exists())

    def test_text_help_text(self):
        """Проверка значения параметра help_text для поля text формы."""
        title_help_text = self.form.fields['text'].help_text
        self.assertEquals(title_help_text, 'Текст нового поста')

    def test_group_help_text(self):
        """Проверка значения параметра help_text для поля group формы."""
        title_help_text = self.form.fields['group'].help_text
        self.assertEquals(title_help_text,
                          'Выберите группу поста или оставьте поле пустым')
