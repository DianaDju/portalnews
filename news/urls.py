from django.urls import path
from . import views
from .views import UpdateProfileView,ProfileDetailView


app_name = 'news'  # Namespace остаётся

urlpatterns = [
    # Смотрим детали профиля и редактируем
    path('profile_detail/', ProfileDetailView.as_view(), name='profile_detail'),
    path('update_profile/', UpdateProfileView.as_view(), name='update_profile'),

    # Все посты (/news/) — без post_type, имя 'all_posts'
    path('', views.news_list, name='all_posts'),

    # Список по типу (/news/news/, /news/article/) — требует post_type
    path('<str:post_type>/', views.news_list, name='news_list'),

    # Детали поста (/news/news/1/, /news/article/1/) — ТЕПЕРЬ С post_type!
    path('<str:post_type>/<int:pk>/', views.news_detail, name='detail'),

    # Создание поста (/news/news/create/, /news/article/create/)
    path('<str:post_type>/create/', views.create_post, name='create'),

    # Редактирование (/news/news/1/edit/, /news/article/1/edit/)
    path('<str:post_type>/<int:pk>/edit/', views.edit_post, name='edit'),

    # Удаление (/news/news/1/delete/, /news/article/1/delete/)
    path('<str:post_type>/<int:pk>/delete/', views.delete_post, name='delete'),

    # Поиск (/news/search/) — как раньше
    path('search/', views.news_search, name='news_search'),

    #path('profile/', ProfileDetailView.as_view(), name='profile'),
    path('<str:post_type>/become-author/', views.become_author, name='become_author'),
]
