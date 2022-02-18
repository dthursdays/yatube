from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='someone')

        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_urls_exist_for_non_authorized(self):
        """Проверяем адреса, доступные неавторизованному пользователю."""

        urls = [
            '/',
            f'/group/{PostsURLTests.test_group.slug}/',
            f'/profile/{PostsURLTests.user}/',
            f'/posts/{PostsURLTests.test_post.id}/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK)

    def test_urls_exist_for_authorized(self):
        """Проверяем адреса, доступные авторизованному пользователю."""

        urls = [
            '/',
            f'/group/{PostsURLTests.test_group.slug}/',
            f'/profile/{PostsURLTests.user}/',
            '/create/',
            f'/posts/{PostsURLTests.test_post.id}/',
            '/follow/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_for_author(self):
        """Проверяем, что страница изменения поста доступна автору."""

        url = f'/posts/{PostsURLTests.test_post.id}/edit/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_redirect_non_author_to_detail(self):
        """Проверяем, что страница изменения поста перенаправляет
         пользователя, не являющегося автором, на страницу с
         информацией о посте."""

        self.user2 = User.objects.create_user(username='someoneelse')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

        url = f'/posts/{PostsURLTests.test_post.id}/edit/'
        response = self.authorized_client2.get(url, follow=True)
        self.assertRedirects(response, f'/posts/{PostsURLTests.test_post.id}/')

    def test_create_url_redirect_non_authorized_to_login(self):
        """Проверяем, что страница создания поста перенаправляет
         неавторизованного пользователя на страницу авторизации."""

        url = '/create/'
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_comment_url_redirect_non_authorized_to_login(self):
        """Проверяем, что страница создания комментария перенаправляет
         неавторизованного пользователя на страницу авторизации."""

        url = f'/posts/{PostsURLTests.test_post.id}/comment/'
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{PostsURLTests.test_post.id}/comment/'
        )

    def test_comment_url_redirect_non_authorized_to_login(self):
        """Проверяем, что страница создания комментария перенаправляет
         авторизованного пользователя на страницу поста."""

        url = f'/posts/{PostsURLTests.test_post.id}/comment/'
        response = self.authorized_client.get(url, follow=True)
        self.assertRedirects(
            response,
            f'/posts/{PostsURLTests.test_post.id}/'
        )

    def test_unexisting_page_url_response_code(self):
        """Проверяем, что запрос к несуществующей
        странице вернёт ошибку 404."""

        url = '/unexisting_page/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostsURLTests.test_post.id}/edit/':
                'posts/create_post.html',
            f'/group/{PostsURLTests.test_group.slug}/':
                'posts/group_list.html',
            f'/posts/{PostsURLTests.test_post.id}/':
                'posts/post_detail.html',
            f'/profile/{PostsURLTests.user}/': 'posts/profile.html'
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
