from django.urls import path
from . import views

app_name = 'articles'  # Namespace для статей

urlpatterns = [
    path('', views.article_list, name='list'),  # Список статей (/articles/)
    path('<int:pk>/', views.article_detail, name='detail'),  # Детальная страница статьи (/articles/1/)
    path('create/', views.article_create, name='create'),  # Создание статьи
    path('<int:pk>/edit/', views.article_edit, name='edit'),  # Редактирование статьи
    path('<int:pk>/delete/', views.article_delete, name='delete'),  # Удаление статьи
]
