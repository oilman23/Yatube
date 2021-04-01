from django.test import TestCase
from posts.models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title="Тестовая группа",
                                         slug="Testovaya-gruppa",)

        cls.post = Post.objects.create(text="какой-то текст здесь присутствует"
                                            ", только для того, чтобы "
                                            "проверить тесты",
                                       author=User.objects.create(
                                           username="vlados"))

    def test_verbose_name(self):
        """Проверяем, что указано удобночитаемое имя для полей формы"""
        field_verboses = {
            "text": "Текст публикации",
            "group": "Группа",
        }
        post = PostModelTest.post
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEquals(post._meta.get_field(value).verbose_name,
                                  expected)

    def test_help_text(self):
        """Проверяем, что указан текст подсказки для полей формы"""
        field_help_texts = {
            "text": "Здесь можно написать всё, что угодно",
            "group": "Запись можно разместить в группе, если это необходимо",
        }
        post = PostModelTest.post
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEquals(post._meta.get_field(value).help_text,
                                  expected)

    def test_str_post(self):
        """Проверяем, что функция __str__ отображает правильный вывод"""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))

    def test_str_group(self):
        """Проверяем, что функция __str__ отображает правильный вывод"""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
