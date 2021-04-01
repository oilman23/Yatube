import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, User, Group, Follow


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title="Заголовок группы",
            slug="test-slug",
        )
        cls.user = User.objects.create(username="adm")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(text="текст поста", group=cls.group,
                                       author=cls.user, image=uploaded)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create(username="vlados")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_follower = User.objects.create(username="follower")
        self.authorized_client_follower = Client()
        self.authorized_client_follower.force_login(self.user_follower)
        self.user_not_follower = User.objects.create(username="heiter")
        self.authorized_client_not_follower = Client()
        self.authorized_client_not_follower.force_login(self.user_not_follower)

    def test_pages_uses_correct_template(self):
        """Проверка на возвращение правильного шаблона к страницам"""
        templates_pages_names = {
            "index.html": reverse("index"),
            "posts/new.html": reverse("new_post"),
            "group.html": reverse("group_posts",
                                  kwargs={"slug": PostPagesTests.group.slug}),
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }
        for template, reverse_name in templates_pages_names.items():
            response = self.authorized_client.get(reverse_name)
            self.assertTemplateUsed(response, template)

    def test_new_post_page_shows_correct_context(self):
        """Проверяем контекст страницы создания нового поста"""
        response = self.authorized_client.get(reverse("new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_page_shows_correct_context(self):
        """Проверяем контекст главной страницы"""
        response = self.authorized_client.get(reverse("index"))
        first_object = response.context.get("page")[0]
        post_group_0 = first_object.group
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(str(post_group_0), PostPagesTests.group.title)
        self.assertEqual(post_text_0, PostPagesTests.post.text)
        self.assertEqual(post_image_0, PostPagesTests.post.image)

    def test_group_posts_pages_show_correct_context(self):
        """Проверяем контекст страницы группы"""
        response = self.authorized_client.get(
            reverse("group_posts", kwargs={"slug": PostPagesTests.group.slug})
        )
        self.assertEqual(response.context["group"].title,
                         PostPagesTests.group.title)
        self.assertEqual(response.context["group"].slug,
                         PostPagesTests.group.slug)
        self.assertEqual(response.context["page"][0].text,
                         PostPagesTests.post.text)
        self.assertEqual(response.context["page"][0].image,
                         PostPagesTests.post.image)

    def test_edit_post_page_shows_correct_context(self):
        """Проверяем контекст страницы редактирования поста"""
        response = (PostPagesTests.authorized_client.get
                    (reverse("post_edit",
                             kwargs={"username": PostPagesTests.post.author,
                                     "post_id": PostPagesTests.post.id})))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        """Проверяем контекст страницы пользователя"""
        response = PostPagesTests.authorized_client.get(
            reverse("profile", kwargs={"username": PostPagesTests.post.author})
        )
        self.assertEqual(response.context["author"].username,
                         PostPagesTests.post.author.username)
        self.assertEqual(response.context["post"].text,
                         PostPagesTests.post.text)
        self.assertEqual(response.context["post"].image,
                         PostPagesTests.post.image)

    def test_post_page_show_correct_context(self):
        """Проверяем контекст страницы отдельного поста"""
        response = PostPagesTests.authorized_client.get(
            reverse("post",
                    kwargs={"username": PostPagesTests.post.author.username,
                            "post_id": PostPagesTests.post.id})
        )
        self.assertEqual(response.context["author"].username,
                         PostPagesTests.post.author.username)
        self.assertEqual(response.context["post"].text,
                         PostPagesTests.post.text)
        self.assertEqual(response.context["post"].image,
                         PostPagesTests.post.image)

    def test_follow_unfollow_authorized_user(self):
        """Проверяем, что авторизованный клиент может подписаться и
        отписаться"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse("profile_follow",
                    kwargs={"username": PostPagesTests.post.author.username}))
        follow_count_after_follow = Follow.objects.count()
        self.assertEqual(follow_count+1, follow_count_after_follow)
        self.authorized_client.get(
            reverse("profile_unfollow",
                    kwargs={"username": PostPagesTests.post.author.username}))
        follow_count_after_unfollow = Follow.objects.count()
        self.assertEqual(follow_count_after_unfollow,
                         follow_count_after_follow-1)

    def test_follow_index(self):
        """Проверяем, что пост у подписанного пользователя появляется в ленте,
        а не у подписанного-нет"""
        Follow.objects.create(user=self.user_follower,
                              author=PostPagesTests.user)
        response_follower = self.authorized_client_follower.get(reverse(
            "follow_index"))
        response_not_follow = self.authorized_client_not_follower.get(reverse(
            "follow_index"))
        self.assertEqual(response_follower.context["page"][0],
                         PostPagesTests.post)
        self.assertFalse(response_not_follow.context["page"])

class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Vlad")
        for number_post in range(12):
            Post.objects.create(
                text=f"Текст поста {number_post}",
                author=cls.user
            )

    def setUp(self):
        self.guest_client = Client()

    def test_count_post_in_index(self):
        """Проверка пагинатора. 10 из 12 постов на первой стр."""
        response = self.guest_client.get(reverse("index"))
        count_objects = len(response.context["page"])
        self.assertEqual(count_objects, 10)

    def test_count_post_in_index_2page(self):
        """Проверка пагинатора. 2 из 12 постов на 2 стр """
        response = self.guest_client.get(reverse("index") + "?page=2")
        count_objects = len(response.context["page"])
        self.assertEqual(count_objects, 2)
