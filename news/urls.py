from django.urls import path
from . import views

app_name = 'news'  # Namespace для URL в шаблонах (например, {% url 'news:detail' pk=news.id %})

urlpatterns = [
    path('', views.news_list, name='list'), # Главная страница: список новостей (/news/)
    path('<int:pk>/', views.news_detail, name='detail'),
    path('search/', views.news_search, name='news_search'),# Детальная страница: новость по ID (/news/1/)
    path('create/', views.news_create, name='create'),  # Создание новости
    path('<int:pk>/edit/', views.news_edit, name='edit'),  # Редактирование новости
    path('<int:pk>/delete/', views.news_delete, name='delete'),  # Удаление новости
]