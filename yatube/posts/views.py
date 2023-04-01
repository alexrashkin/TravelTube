from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from posts.services import make_pages
from yatube.settings import NUMBER_POSTS

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow, Image, PostImage


def index(request):
    posts = Post.objects.all().order_by('-pub_date')
    page_obj = make_pages(request, posts, NUMBER_POSTS)
    context = {
        'page_obj': page_obj,
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by('-pub_date')
    page_obj = make_pages(request, post_list, NUMBER_POSTS)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author
    )
    post_list = author.posts.select_related('group')
    page_obj = make_pages(request, post_list, NUMBER_POSTS)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    template = 'posts/post_detail.html'
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def create_post(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        # Обработка множественных изображений
        images = request.FILES.getlist('images')
        # Получение списка изображений
        for image_file in images:
            image = Image(Image=image_file)
            image.save()
            # Сохранение объекта Image
            post_image = PostImage(post=post, image=image)
            post_image.save()
        return redirect('posts:profile', username=post.author.username)
    else:
        print(form.errors)
    return render(request, 'posts/create_post.html',
                  {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    form = PostForm(instance=post)
    context = {
        'is_edit': True,
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
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
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = make_pages(request, posts, NUMBER_POSTS)
    context = {
        'page_obj': page_obj,
        'follow': True,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts:profile'
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(template, author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts:profile'
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(template, author)
