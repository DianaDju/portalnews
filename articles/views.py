from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from news.models import Post
from news.forms import PostForm

def article_list(request):
    articles = Post.objects.filter(post_type='AR').order_by('-time_created')  # Список статей
    return render(request, 'articles/list.html', {'articles': articles})

def article_detail(request, pk):
    article = get_object_or_404(Post, pk=pk, post_type='AR')
    return render(request, 'articles/detail.html', {'article': article})

def article_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.post_type = 'AR'  # Фиксируем тип как статья
            post.save()
            messages.success(request, 'Статья создана!')
            return redirect('articles:detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'articles/create.html', {'form': form})

def article_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, post_type='AR')  # Только статьи
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья обновлена!')
            return redirect('articles:detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'articles/edit.html', {'form': form, 'post': post})

def article_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, post_type='AR')  # Только статьи
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Статья удалена!')
        return redirect('articles:list')
    return render(request, 'articles/delete.html', {'post': post})

