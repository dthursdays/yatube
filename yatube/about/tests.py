from django.test import Client, TestCase
from http import HTTPStatus


class PostsURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_urls_exist(self):
        """Проверяем адреса, доступные неавторизованному пользователю."""

        urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        url_templates_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
