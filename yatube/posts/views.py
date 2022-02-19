from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import pagination


def index(request):
    template = 'posts/index.html'

    page_number = request.GET.get('page')
    post_list = Post.objects.select_related('author', 'group')
    page_obj = pagination(page_number, post_list)

    context = {
        'index': True,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_list(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)

    post_list = group.posts.select_related('author')
    page_number = request.GET.get('page')
    page_obj = pagination(page_number, post_list)

    context = {
        'group': group,
        'page_obj': page_obj
    }

    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)

    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()

    post_list = author.posts.select_related('group')
    page_number = request.GET.get('page')
    page_obj = pagination(page_number, post_list)

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }

    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    author = post.author

    comments = post.comments.select_related()

    form = CommentForm(request.POST or None)

    user_can_edit = False
    if post.author == request.user:
        user_can_edit = True

    context = {
        'author': author,
        'post': post,
        'user_can_edit': user_can_edit,
        'form': form,
        'comments': comments
    }

    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)

    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'form': form,
        'user_can_edit': True,
        'post_id': post_id
    }

    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'

    follows = request.user.follower.select_related()
    authors = User.objects.filter(following__in=follows)
    post_list = Post.objects.filter(author__in=authors)

    page_number = request.GET.get('page')
    page_obj = pagination(page_number, post_list)

    context = {
        'follow': True,
        'page_obj': page_obj,
    }

    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
        return redirect('posts:follow_index')
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect('posts:follow_index')
