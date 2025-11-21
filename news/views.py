from django.shortcuts import render, get_object_or_404
from .models import Post



def news_list(request):
    """Отображает список новостей, отсортированный от новых к старым.

        Фильтрует только посты типа 'N' (новости). Передает в шаблон для рендеринга."""

    # Список только новостей (post_type='N'), сортировка от новых к старым
    news_list = Post.objects.filter(post_type='N').order_by('-time_created')  # type: ignore[attr-defined]
    context = {'news_list': news_list}
    return render(request, 'news_list.html', context)


def news_detail(request, pk):
    """Отображает детальную страницу новости по ID (pk).

       Получает объект новости или 404, если не найдена. Форматирует дату для отображения."""
    # Получение новости по ID, только типа 'N'; 404 если не существует
    news = get_object_or_404(Post, id=pk, post_type='N')
    # Форматирование даты создания в вид 'день.месяц.год
    formatted_date = news.time_created.strftime('%d.%m.%Y')
    context = {'news': news, 'formatted_date': formatted_date}
    return render(request, 'news_detail.html', context)