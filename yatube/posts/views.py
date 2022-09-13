from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


def index(request):
    """Функция index передает словарь context в шаблон posts/index.html.
     В словаре хранится выборка из кол-ва постов равных значению
     COUNT_OF_POSTS, сгруппированная по убыванию даты.
     Также в context передается значение поля title страницы html.
     """
    post_list = Post.objects.select_related('author', 'group').all()
    paginator = Paginator(post_list, settings.COUNT_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Функция group_posts передает словарь context в шаблон
    posts/group_list.html. В словаре хранится выборка из кол-ва постов равных
    значению COUNT_OF_POSTS, отфильтрованная по наименованию группы и
    сгруппированная по убыванию даты. Функция проверяет наличие соответствующей
    группы в БД по значению slug в запросе. Также в context передается значение
    поля title страницы html.
     """
    group = get_object_or_404(Group, slug=slug)
    post_group_list = group.posts.select_related('author').all()
    paginator = Paginator(post_group_list, settings.COUNT_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Записи сообщества:'
    context = {
        'page_obj': page_obj,
        'group': group,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Функция profile передает словарь context в шаблон posts/profile.html
       все посты пользователя."""
    author = get_object_or_404(User, username=username)
    post_author = author.posts.prefetch_related('group').all()
    count_posts = post_author.count()
    paginator = Paginator(post_author, settings.COUNT_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        following = Follow.objects.filter(user=user, author=author).exists()
    else:
        following = True
    context = {
        'author': author,
        'page_obj': page_obj,
        'count_posts': count_posts,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Функция post_detail передает словарь context в шаблон
       posts/post_detail.html всю информацию о конкретном посте."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = Comment.objects.filter(post=post_id).select_related('author')
    count_posts = Post.objects.filter(author=post.author).count()
    context = {
        'post': post,
        'count_posts': count_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Функция post_create передает форму PostForm в шаблон
       posts/create_post.html для создания нового поста."""
    title = 'Новый пост'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'title': title})


@login_required
def post_edit(request, post_id):
    """Функция post_edit передает заполненную форму PostForm в шаблон
       posts/create_post.html для редактирования текущего поста."""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'title': 'Редактировать пост',
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Функция add_comment передает заполненную форму CommentForm в шаблон
           posts/post_detail.html для создания нового комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Функция follow_index передает словарь context в шаблон
    posts/follow.html. В словаре хранится выборка из постов авторов на которых
    подписан пользователь"""
    user = request.user
    post_follow_list = Post.objects.filter(
        author__following__user=user).select_related('author', 'group')
    paginator = Paginator(post_follow_list, settings.COUNT_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Мои подписки'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Функция profile_follow создает в БД запись об имени пользователя и об
    авторе на которого подписался пользователь"""
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Функция profile_unfollow удаляет из БД запись об имени пользователя и об
       авторе на которого подписался пользователь"""
    user = request.user
    author = get_object_or_404(User, username=username)
    unfollow_author = Follow.objects.filter(user=user, author=author)
    unfollow_author.delete()
    return redirect('posts:profile', username=username)
