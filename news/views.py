from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .forms import SearchForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Author
from .forms import PostForm





def news_list(request, post_type=None):
    if post_type:  # Если post_type передан (фильтр по типу: /news/news/ или /news/article/)
        posts = Post.objects.filter(post_type=post_type).order_by('-time_created')
        is_filtered = True
        page_obj = None  # Без пагинации для фильтрованных
    else:  
        posts = Post.objects.all().order_by('-time_created')  # Все посты: новости + статьи
        is_filtered = False
        paginator = Paginator(posts, 10)  # 10 постов на страницу
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'posts': posts if post_type else None,  # Для фильтрованных — полный список
        'page_obj': page_obj, 
        'post_type': post_type,
        'is_filtered': is_filtered,
    }
    return render(request, 'news/news_list.html', context)


def news_detail(request,post_type, pk):
    """Отображает детальную страницу новости по ID (pk).

       Получает объект новости или 404, если не найдена. Форматирует дату для отображения."""


    post = get_object_or_404(Post, pk=pk, post_type=post_type)
    return render(request, 'news/news_detail.html', {'post': post})



def news_search(request):
    form = SearchForm(request.GET or None)  # Форма получает данные из GET
    posts = Post.objects.all().order_by('-time_created')

    if form.is_valid():
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        date_from = form.cleaned_data.get('date_from')

       
        query = Q()
        if title:
            query &= Q(title__icontains=title)  # Поиск по названию (регистронезависимый)
        if author:
            query &= Q(author__author_user__username__icontains=author)  # Поиск по username автора
        if date_from:
            query &= Q(time_created__date__gte=date_from)  # Позже даты (date >= date_from)

        posts = posts.filter(query)  # Применяем фильтр

    # Пагинация для результатов поиска (10 на страницу)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/search.html', {'form': form, 'page_obj': page_obj})


@login_required
def create_post(request, post_type):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            author = post.author
            author.update_rating()
            post.post_type = post_type  # Устанавливаем post_type из URL
            post.save()
            return redirect('news:detail', post_type=post.post_type, pk=post.pk)  # Редирект на detail созданного поста
    else:
        form = PostForm()

    context = {
        'form': form,
        'post_type': post_type,  # Передаём post_type в шаблон
    }
    return render(request, 'news/create.html', context)



@login_required
def edit_post(request, post_type, pk):
    post = get_object_or_404(Post, pk=pk, post_type=post_type)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            author = post.author
            author.update_rating()
            return redirect('news:detail', post_type=post.post_type, pk=post.pk)
    else:
        form = PostForm(instance=post)
    context = {'form': form, 'post': post, 'post_type': post_type}
    return render(request, 'news/edit.html', context)


# Удаление (общее)
@login_required
def delete_post(request, post_type, pk):
    post = get_object_or_404(Post, pk=pk, post_type=post_type)  # Фильтр по post_type
    if request.method == 'POST':  # Подтверждение удаления
        author = post.author
        post.delete()  # Удаляем пост
        author.update_rating()  # Обновляем рейтинг автора (комментарии/посты пересчитаются)
        return redirect('news_list')  
    context = {
        'post': post,
        'post_type': post_type  # Добавляем явно из URL
    }
    return render(request, 'news/delete.html', context)


