from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import reverse

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("group_posts", kwargs={"slug": self.slug})


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст публикации",
        help_text="Здесь можно написать всё, что угодно"
    )
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, related_name="posts", blank=True,
        null=True, verbose_name="Группа",
        help_text="Запись можно разместить в группе, если это необходимо"
    )
    image = models.ImageField(
        upload_to="posts/", blank=True, null=True,
        verbose_name="Картинка поста"
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]


class Comment(models.Model):
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Здесь можно написать весь ваш хейт, "
                  "похвалу или конструктивную критику"
    )
    created = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments",
        verbose_name="Пост", help_text="Комментарий можно оставить "
                                       "к любому посту"
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "author"],
                                    name="unique follow")
        ]
