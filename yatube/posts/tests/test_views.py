import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post
from ..views import POSTS_ON_PAGE

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='someone')

        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.other_test_group = Group.objects.create(
            title='Другая группа',
            slug='other_slug',
            description='Тестовое описание',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.test_group,
            image=cls.image
        )

        cls.comment = Comment.objects.create(
            text='Текст комментария',
            author=cls.user,
            post_id=cls.group_post.id
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user)

    def test_cache_index_page(self):
        """Кэширование работает."""

        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        cache_check = response.content

        self.some_post = Post.objects.create(
            text='Тестовый текст',
            author=PostsPagesTests.user
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, cache_check)

        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, cache_check)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': PostsPagesTests.test_group.slug}):
                        'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': PostsPagesTests.user}):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostsPagesTests.group_post.id}):
                        'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsPagesTests.group_post.id}):
                        'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }

        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse('posts:index'))

        post = response.context.get('page_obj')[0]
        self.assertEqual(post, PostsPagesTests.group_post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsPagesTests.group_post.group.slug}))

        post = response.context.get('page_obj')[0]
        self.assertEqual(post, PostsPagesTests.group_post)
        group = response.context.get('group')
        self.assertEqual(group, PostsPagesTests.group_post.group)

    def test_group_list_not_show_other_group_post(self):
        """Пост не попал в группу, для которой не был предназначен."""

        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostsPagesTests.other_test_group.slug}))

        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostsPagesTests.group_post.author}))

        post = response.context.get('page_obj')[0]
        self.assertEqual(post, PostsPagesTests.group_post)
        author = response.context.get('author')
        self.assertEqual(author, PostsPagesTests.group_post.author)

    def test_profile_not_show_other_profile_post(self):
        """В шаблоне profile нет поста, относящегося к другому пользователю."""

        self.other_user = User.objects.create_user(username='someone_else')

        self.other_user_test_post = Post.objects.create(
            text='Тестовый текст',
            author=self.other_user,
        )

        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostsPagesTests.group_post.author}))

        self.assertEqual(len(response.context['page_obj']), 1)

    def test_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsPagesTests.group_post.id}))

        post = response.context.get('post')
        self.assertEqual(post, PostsPagesTests.group_post)
        author = response.context.get('author')
        self.assertEqual(author, PostsPagesTests.group_post.author)
        user_can_edit = response.context.get('user_can_edit')
        self.assertEqual(user_can_edit, True)
        comment = response.context.get('comments')[0]
        self.assertEqual(comment, PostsPagesTests.comment)
        form_initial = response.context.get('form').initial
        self.assertEqual(form_initial, {})

    def test_detail_show_correct_user_can_edit(self):
        """Переменная user_can_edit == False для пользователя, не являющегося
        автором поста."""

        self.other_user = User.objects.create_user(username='someone_else')
        self.other_client = Client()
        self.other_client.force_login(self.other_user)

        response = self.other_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsPagesTests.group_post.id}))

        user_can_edit = response.context.get('user_can_edit')
        self.assertEqual(user_can_edit, False)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostsPagesTests.group_post.id}))

        form_text = response.context.get('form').initial['text']
        self.assertEqual(form_text, PostsPagesTests.group_post.text)
        user_can_edit = response.context.get('user_can_edit')
        self.assertEqual(user_can_edit, True)
        post_id = response.context.get('post_id')
        self.assertEqual(post_id, PostsPagesTests.group_post.id)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create передает пустую форму."""

        response = self.authorized_client.get(reverse('posts:post_create'))

        form_initial = response.context.get('form').initial
        self.assertEqual(form_initial, {})


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='someone')

        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        for i in range(POSTS_ON_PAGE + 3):
            Post.objects.create(
                text='Тестовый текст',
                author=cls.user,
                group=cls.test_group,
            )

    def setUp(self):
        self.client = Client()
        self.posts_number = Post.objects.count()
        self.profile_posts_number = Post.objects.filter(
            author=PaginatorViewsTest.user).count()
        self.test_group_posts_number = Post.objects.filter(
            group=PaginatorViewsTest.test_group).count()

    def test_index_first_page_contains_ten_records(self):
        """Первая страница index содержит views.POSTS_ON_PAGE постов."""

        response = self.client.get(reverse('posts:index'))

        self.assertEqual(len(response.context['page_obj']), POSTS_ON_PAGE)

    def test_index_second_page_contains_three_records(self):
        """Вторая страница index содержит правильное число постов."""

        response = self.client.get(reverse('posts:index') + '?page=2')
        self.second_page_posts_qty = self.posts_number - POSTS_ON_PAGE

        if self.second_page_posts_qty > POSTS_ON_PAGE:
            self.second_page_posts_qty = POSTS_ON_PAGE

        self.assertEqual(
            len(response.context['page_obj']),
            self.second_page_posts_qty)

    def test_group_list_first_page_contains_ten_records(self):
        """Первая страница group_list содержит views.POSTS_ON_PAGE постов."""

        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PaginatorViewsTest.test_group.slug}))

        self.assertEqual(len(response.context['page_obj']), POSTS_ON_PAGE)

    def test_group_list_second_page_contains_three_records(self):
        """Вторая страница group_list содержит правильное число постов."""

        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PaginatorViewsTest.test_group.slug}) + '?page=2')

        self.second_page_posts_qty = (self.test_group_posts_number
                                      - POSTS_ON_PAGE)

        if self.second_page_posts_qty > POSTS_ON_PAGE:
            self.second_page_posts_qty = POSTS_ON_PAGE

        self.assertEqual(
            len(response.context['page_obj']),
            self.second_page_posts_qty)

    def test_profile_first_page_contains_ten_records(self):
        """Первая страница profile содержит views.POSTS_ON_PAGE постов."""

        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': PaginatorViewsTest.user}))

        self.assertEqual(len(response.context['page_obj']), POSTS_ON_PAGE)

    def test_profile_second_page_contains_three_records(self):
        """Вторая страница profile содержит правильное число постов."""

        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': PaginatorViewsTest.user}) + '?page=2')

        self.second_page_posts_qty = (self.profile_posts_number
                                      - POSTS_ON_PAGE)

        if self.second_page_posts_qty > POSTS_ON_PAGE:
            self.second_page_posts_qty = POSTS_ON_PAGE

        self.assertEqual(
            len(response.context['page_obj']),
            self.second_page_posts_qty)


class PostsFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='someone')
        cls.user2 = User.objects.create(username='someoneelse')
        cls.user3 = User.objects.create(username='theguy')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsFollowTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(PostsFollowTests.user2)

    def test_follow_button_creates_and_deletes_follow(self):
        """Кнопки подписка/отписка создают и удаляют объект подписки."""

        def check_follow_exists():
            return Follow.objects.filter(
                user=PostsFollowTests.user,
                author=PostsFollowTests.user2
            ).exists()

        self.assertFalse(check_follow_exists())

        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostsFollowTests.user2}))

        self.assertTrue(check_follow_exists())

        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': PostsFollowTests.user2}))

        self.assertFalse(check_follow_exists())

    def test_follow_show_correct_context(self):
        """Шаблон follow сформирован с правильным контекстом"""

        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostsFollowTests.user3}))

        self.user3_post = Post.objects.create(
            text='Тестовый текст',
            author=PostsFollowTests.user3
        )

        response = self.authorized_client.get(reverse('posts:follow_index'))
        try:
            post = response.context.get('page_obj')[0]
        except IndexError:
            post = None
        self.assertEqual(post, self.user3_post)

        response = self.authorized_client2.get(reverse('posts:follow_index'))
        try:
            post = response.context.get('page_obj')[0]
        except IndexError:
            post = None
        self.assertNotEqual(post, self.user3_post)
