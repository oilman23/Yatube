from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator

from .forms import PostForm, CommentForm, GroupForm
from .models import Group, Post, User, Follow


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts_list = group.posts.all()
    paginator = Paginator(group_posts_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, "posts/new.html", {"form": form,
                                                  "is_new": True})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")


@login_required
def new_group(request):
    form = GroupForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, "posts/group_new.html", {"form": form,
                                                  "is_new": True})
    group = form.save(commit=False)
    group.save()
    return redirect("index")


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts_list = author.posts.all()
    paginator = Paginator(user_posts_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = (request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author__username=username).exists())
    context = {
        "author": author,
        "page": page,
        "following": following
    }
    return render(request, "posts/profile.html", context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        "post": post,
        "author": post.author,
        "comments": comments,
        "form": form
    }
    return render(request, "posts/post.html", context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author != request.user:
        return redirect("post", username, post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect("post", username, post_id)

    return render(request, "posts/new.html", {"form": form, 'post': post})


@login_required
def post_delete(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author != request.user:
        return redirect("post", username, post_id)
    post.delete()
    return redirect("profile", username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if not form.is_valid():
        return render(request, "posts/post.html",
                      {"form": form, "post": post, "author": post.author})
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect("post", username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("profile", username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("profile", username)
