from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, User, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title="Тестовый заголовок",
            slug="test-slug",
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="Vlad23")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(text="Текст", author=self.user,)
        self.user_not_author = User.objects.create_user(username="Maks")
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)
        self.profile_url = reverse("profile",
                                   kwargs={"username": self.user.username})
        self.post_user_url = (reverse
                              ("post",
                               kwargs={"username": self.post.author.username,
                                       "post_id": self.post.id}))
        self.post_user_edit_url = (
            reverse("post_edit", kwargs={"username": self.post.author.username,
                                         "post_id": self.post.id}))
        self.post_comment_url = (
            reverse("add_comment",
                    kwargs={"username": self.post.author.username,
                            "post_id": self.post.id}))

    def test_authorized_client_status_code(self):
        """Проверяем статус код страниц для авторизованного пользователя"""
        urls_status_code = {
            "/": 200,
            "/group/test-slug/": 200,
            "/new/": 200,
            self.profile_url: 200,
            self.post_user_url: 200,
            self.post_user_edit_url: 200,
            self.post_comment_url: 200,
        }
        for urls, st_code in urls_status_code.items():
            with self.subTest():
                response = self.authorized_client.get(urls)
                self.assertEqual(response.status_code, st_code)

    def test_authorized_client_not_author_status_code(self):
        """Проверяем статус код страницы для авторизованного пользователя
        (не автора поста)"""
        response = (self.authorized_client_not_author.get
                    (self.post_user_edit_url))
        self.assertEqual(response.status_code, 302)

    def test_guest_client_status_code(self):
        """Проверяем статус код страниц для неавторизованного пользователя"""
        urls_status_code = {
            "/": 200,
            "/group/test-slug/": 200,
            "/about/author/": 200,
            "/about/tech/": 200,
            "/new/": 302,
            self.post_user_edit_url: 302,
            self.post_comment_url: 302,
            "/djulieta/": 404,
        }
        for urls, st_code in urls_status_code.items():
            with self.subTest():
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, st_code)

    def test_urls_uses_correct_template(self):
        """Проверяем правильность передаваемого шаблона для страниц сайта"""
        templates_url_names = {
            "index.html": "/",
            "group.html": "/group/test-slug/",
            "posts/new.html": "/new/",
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        response = self.authorized_client.get(self.post_user_edit_url)
        self.assertTemplateUsed(response, "posts/new.html")

    def test_redirect(self):
        """Проверяем корректность работы редиректа при попытке редактировать
        пост не автором поста"""
        response = (self.authorized_client_not_author.get
                    (self.post_user_edit_url))
        self.assertRedirects(response, self.post_user_url)
