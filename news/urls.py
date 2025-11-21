from django.urls import path
from . import views

app_name = 'news'  # Namespace для URL в шаблонах (например, {% url 'news:detail' pk=news.id %})

urlpatterns = [
    path('', views.news_list, name='list'), # Главная страница: список новостей (/news/)
    path('<int:pk>/', views.news_detail, name='detail'),   # Детальная страница: новость по ID (/news/1/)
]