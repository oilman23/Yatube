from django.forms import ModelForm
from .models import Post, Comment
from django import forms


class PostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].empty_label = "Группа не выбрана"

    class Meta:
        model = Post
        fields = ("text", "group", "image")


class CommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = ("text", )
        widget = {"text": forms.Textarea}

