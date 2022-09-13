from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Pupkin')
        cls.group = Group.objects.create(
            title='Собаки',
            slug='dogs',
            description='Пост о собаках',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Собака - это друг человека.',
        )

    def test_group_models_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, group.__str__())

    def test_post_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = self.post
        expected_object_name = post.text[:settings.OUTPUT_ELEMENTS_OF_POSTS]
        self.assertEqual(expected_object_name, post.__str__())

    def test_group_verbose_name(self):
        """verbose_name у модели Group в полях совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Группа',
            'slug': 'Путь',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_post_verbose_name(self):
        """verbose_name у модели Post в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Пост',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
