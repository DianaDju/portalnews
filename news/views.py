from django.core.paginator import Paginator
from django.db.models import Q
from .forms import SearchForm, PostForm
from .models import Post, Author, Category, CategorySubscription
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from django.urls import reverse_lazy
from .forms import SubscribeCategoryForm, UnsubscribeCategoryForm




def news_list(request, post_type=None):
    is_filtered = False
    post_type = post_type
    is_author = request.user.is_authenticated and request.user.groups.filter(name='authors').exists()
    categories = Category.objects.all()

    if post_type:  # Если post_type передан (фильтр по типу: /news/news/ или /news/article/)
        posts = Post.objects.filter(post_type=post_type).order_by('-time_created')
        is_filtered = True
        page_obj = None
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
        'is_author': is_author,
        'categories': categories,
    }
    return render(request, 'news/news_list.html', context)


def news_detail(request, post_type, pk):
    """Отображает детальную страницу новости по ID (pk).

       Получает объект новости или 404, если не найдена. Форматирует дату для отображения."""

    post = get_object_or_404(Post, pk=pk, post_type=post_type)
    return render(request, 'news/news_detail.html', {'post': post})


def news_search(request):
    form = SearchForm(request.GET or None)
    posts = Post.objects.all().order_by('-time_created')

    if form.is_valid():
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        date_from = form.cleaned_data.get('date_from')

        query = Q()
        if title:
            query &= Q(title__icontains=title)
        if author:
            query &= Q(author__author_user__username__icontains=author)
        if date_from:
            query &= Q(time_created__date__gte=date_from)

        posts = posts.filter(query)  # Применяем фильтр

    # Пагинация для результатов поиска (10 на страницу)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/search.html', {'form': form, 'page_obj': page_obj})

@login_required  # Обеспечивает аутентификацию
@permission_required('news.add_post')
def create_post(request, post_type):

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.author_profile
            post.post_type = post_type
            post.save()
            # Обновляем рейтинг автора ПОСЛЕ сохранения поста
            if hasattr(post.author, 'update_rating'):  # Безопасная проверка
                post.author.update_rating()
            messages.success(request, 'Пост создан!')
            return redirect('news:detail', post_type=post.post_type, pk=post.pk)
    else:
        form = PostForm(initial={'post_type': post_type})  # Передаём initial для формы

    context = {
        'form': form,
        'post_type': post_type,
    }

    return render(request, 'news/create.html', context)

@permission_required('news.change_post')
def edit_post(request, post_type, pk):
    post = get_object_or_404(Post, pk=pk, post_type=post_type)

    if not (request.user == post.author.author_user or request.user.has_perm('news.can_edit_post')):
        raise PermissionDenied("You do not have permission to edit this post.")

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


def delete_post( request, post_type, pk):
    post = get_object_or_404(Post, pk=pk, post_type=post_type)  # Фильтр по post_type
    if request.method == 'POST':  # Подтверждение удаления
        author = post.author
        post.delete()  # Удаляем пост
        author.update_rating()  # Обновляем рейтинг автора (комментарии/посты пересчитаются)
        return redirect('news:news_list', post_type=post_type)
    context = {
        'post': post,
        'post_type': post_type  # Добавляем явно из URL
    }
    return render(request, 'news/delete.html', context)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'news/profile_detail.html'  # Правильный шаблон
    context_object_name = 'user_profile'

    def get_object(self, queryset=None):
        # Возвращает профиль текущего пользователя (только свой профиль)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class UpdateProfileView(LoginRequiredMixin, UpdateView):
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        template_name = 'news/update_profile.html'
        success_url = reverse_lazy('news:profile_detail')

        def get_object(self, queryset=None):
            return self.request.user







@receiver(post_save, sender=User)
def add_to_common(sender, instance, created, **kwargs):
    if created:
        common_group = Group.objects.get(name='common')
        instance.groups.add(common_group)


@login_required  # Только для залогиненных пользователей
def become_author(request,post_type):
    if request.method == 'POST':
        authors_group, created = Group.objects.get_or_create(name='authors')
        request.user.groups.add(authors_group)
        Author.objects.get_or_create(author_user=request.user)

        content_type = ContentType.objects.get_for_model(Post)
        add_perm = Permission.objects.get(content_type=content_type, codename='add_post')
        edit_perm = Permission.objects.get(content_type=content_type, codename='change_post')
        authors_group.permissions.add(add_perm, edit_perm)

        messages.success(request, 'Вы стали автором!')


        return redirect('news:news_list', post_type=post_type)


    return redirect('news:news_list', post_type=post_type)



class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'news/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object

        if category:
            # Список последних 10 опубликованных постов категории
            context['posts'] = Post.objects.filter(
                categories=category,
                is_published=True
            ).order_by('-time_created')[:10]

            # Проверка подписки пользователя на категорию
            context['is_subscribed'] = CategorySubscription.objects.filter(
                user=self.request.user,
                category=category
            ).exists()

            # Получаем объект подписки, если он есть
            context['subscription'] = CategorySubscription.objects.filter(
                user=self.request.user,
                category=category
            ).first()

        return context


@login_required
def subscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if CategorySubscription.objects.filter(user=request.user, category=category).exists():
        messages.warning(request, 'Вы уже подписаны на эту категорию.')
    else:
        try:
            subscription = CategorySubscription.objects.create(user=request.user, category=category)
            messages.success(request, f'Вы успешно подписались на категорию "{category.name_category}".')
        except Exception as e:
            messages.error(request, f'Ошибка при подписке: {e}')
    return redirect('news:category-detail', pk=category.id)


@login_required
def unsubscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subscription = get_object_or_404(
        CategorySubscription,
        user=request.user,
        category=category
    )
    form = UnsubscribeCategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        subscription.delete()
        messages.success(request, f'Вы отписались от категории "{category.name_category}".')
    else:
        messages.error(request, 'Ошибка при отписке.')
    return redirect('news:category-detail', pk=category.id)




class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'news/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Если не опубликован — 404 (опционально)
        if not obj.is_published:
            from django.http import Http404
            raise Http404("Пост не опубликован.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.all().order_by('-time_created')
        return context
