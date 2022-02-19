import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='someone')

        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            image=None
        )

        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        self.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        """Валидная форма создает новый пост."""

        posts_count = Post.objects.count()

        form_data = {
            'group': PostFormTests.test_group.id,
            'text': 'Тестовый текст',
            'image': self.image
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.order_by('-id')[0]

        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            last_post.text == form_data['text']
        )

        self.assertTrue(
            last_post.group.id == form_data['group']
        )

        self.assertTrue(
            last_post.image == f'posts/{self.image.name}'
        )

        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': PostFormTests.user}))

    def test_cant_create_empty_post(self):
        """Пустая форма не создает новый пост."""
        posts_count = Post.objects.count()

        form_data = {
            'text': ''
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )

        self.assertEqual(Post.objects.count(), posts_count)

        self.assertFormError(
            response,
            'form',
            'text',
            'поле должно быть заполнено'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма изменяет пост в базе данных."""

        self.other_group = Group.objects.create(
            title='Другая группа',
            slug='other_slug',
            description='Тестовое описание')

        new_small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        self.other_image = SimpleUploadedFile(
            name='new_small.gif',
            content=new_small_gif,
            content_type='image/gif'
        )

        form_data = {
            'group': self.other_group.id,
            'text': 'Новый тестовый текст',
            'image': self.other_image
        }

        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostFormTests.test_post.id}),

            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(id=PostFormTests.test_post.id)

        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': PostFormTests.test_post.id}))

        self.assertTrue(edited_post.text == form_data['text'])

        self.assertTrue(edited_post.group.id == form_data['group'])

        self.assertTrue(
            edited_post.image == f'posts/{self.other_image.name}'
        )

    def test_cant_edit_to_empty_post(self):
        """Пустая форма не изменяет пост."""

        form_data = {
            'text': ''
        }

        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostFormTests.test_post.id}),

            data=form_data
        )
        edited_post = Post.objects.get(id=PostFormTests.test_post.id)

        self.assertTrue(edited_post.text == PostFormTests.test_post.text)

        self.assertFormError(
            response,
            'form',
            'text',
            'поле должно быть заполнено'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_comment(self):
        """Валидная форма создает новый комментарий."""

        comments_count = Comment.objects.count()

        form_data = {
            'text': 'Тестовый текст'
        }

        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': PostFormTests.test_post.id}),

            data=form_data,
            follow=True
        )
        last_comment = Comment.objects.order_by('-id')[0]

        self.assertEqual(Comment.objects.count(), comments_count + 1)

        self.assertTrue(
            last_comment.text == form_data['text']
        )

        self.assertTrue(
            last_comment.post == PostFormTests.test_post
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': PostFormTests.test_post.id}))

    def test_cant_create_empty_comment(self):
        """Пустая форма не создает новый комментарий."""
        comments_count = Comment.objects.count()

        form_data = {
            'text': ''
        }

        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': PostFormTests.test_post.id}),

            data=form_data
        )

        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
