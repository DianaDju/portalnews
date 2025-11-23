from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .forms import SearchForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Post
from .forms import PostForm



def news_list(request):
    """Отображает список новостей, отсортированный от новых к старым.

        Фильтрует только посты типа 'N' (новости). Передает в шаблон для рендеринга."""


    news_list = Post.objects.all().order_by('-time_created')  # type: ignore[attr-defined]
    # Создаем Paginator: news_list — список, 10 — сколько новостей на страницу
    paginator = Paginator(news_list, 10)

    # Получаем номер страницы из URL (например, /news/?page=2)
    page = request.GET.get('page')

    try:
        news = paginator.page(page)  # Получаем новости для этой страницы
    except PageNotAnInteger:
        news = paginator.page(1)  # Если номер страницы не число, показываем первую
    except EmptyPage:
        news = paginator.page(paginator.num_pages)  # Если страница пустая, показываем последнюю

    context = {'news': news, 'paginator': paginator}
    return render(request, 'news_list.html', context)


def news_detail(request, pk):
    """Отображает детальную страницу новости по ID (pk).

       Получает объект новости или 404, если не найдена. Форматирует дату для отображения."""
    # Получение новости по ID, только типа 'N'; 404 если не существует
    news = get_object_or_404(Post, id=pk, post_type='NW')
    # Форматирование даты создания в вид 'день.месяц.год
    formatted_date = news.time_created.strftime('%d.%m.%Y')
    context = {'news': news, 'formatted_date': formatted_date}
    return render(request, 'news_detail.html', context)

def news_search(request):
    form = SearchForm(request.GET or None)  # Форма получает данные из GET
    posts = Post.objects.all().order_by('-time_created')

    if form.is_valid():
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        date_from = form.cleaned_data.get('date_from')

        # Строим фильтр с Q для комбинации критериев
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




def news_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.post_type = 'NW'  # Фиксируем тип как новость
            post.save()
            messages.success(request, 'Новость создана!')
            return redirect('news:detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'news/create.html', {'form': form})

def news_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, post_type='NW')  # Только новости
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новость обновлена!')
            return redirect('news:detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'news/edit.html', {'form': form, 'post': post})

def news_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, post_type='NW')  # Только новости
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Новость удалена!')
        return redirect('news:list')
    return render(request, 'news/delete.html', {'post': post})

