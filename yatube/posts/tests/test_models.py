from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_strs = {
            str(PostsModelsTest.group): PostsModelsTest.group.title,
            str(PostsModelsTest.post): PostsModelsTest.post.text[:15],
        }
        for model_str, expected_value in models_strs.items():
            with self.subTest(model_str=model_str):
                self.assertEqual(
                    model_str, expected_value)

    def test_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        post = PostsModelsTest.post
        field_verboses = {
            'text': 'Текст поста',
            'group': 'Группа',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        post = PostsModelsTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
