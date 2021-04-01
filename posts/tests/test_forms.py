import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User, Group


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title="Заголовок группы",
            slug="test-slug",
        )
        cls.user = User.objects.create(username="vlados")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(text="текст поста", group=cls.group,
                                       author=cls.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_check_create_post(self):
        """Проверяем наличие в БД созданного поста"""
        posts_count = Post.objects.count()
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
        form_data = {
            "text": "Текст из формы",
            "image": uploaded
        }
        response = PostFormTests.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_edit_existing_post(self):
        """Проверяем изменились ли данные и не создался ли новый обьект в БД
        при редактировании поста"""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Новый текст из формы",
        }
        response = PostFormTests.authorized_client.post(
            reverse("post_edit",
                    kwargs={"username": PostFormTests.user.username,
                            "post_id": PostFormTests.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.last().text,
                         form_data["text"])
        self.assertEqual(response.status_code, 200)
