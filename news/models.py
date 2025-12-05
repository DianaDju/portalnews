from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse


class Author(models.Model):
    """Модель автора, связанная с пользователем Django. Хранит рейтинг автора на основе постов и комментариев."""
    author_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    rating_author = models.SmallIntegerField(default=0)  # Рейтинг автора, обновляется автоматически

    def __str__(self):
        return self.author_user.username

    def update_rating(self):
        """ Обновляет рейтинг автора на основе сумм рейтингов его постов и комментариев.

            Расчёт: (рейтинг постов * 3) + рейтинг комментариев автора + рейтинг комментариев к его постам. """

        from django.db.models import Sum
        # Сумма рейтингов постов автора
        post_sum = self.post_set.aggregate(total=Sum('rating'))['total'] or 0 # type: ignore[attr-defined]
        # Сумма рейтингов комментариев автора
        author_comments_sum = Comment.objects.filter(comment_user=self.author_user).aggregate(total=Sum('rating'))['total'] or 0
        # Сумма рейтингов комментариев к постам автора
        post_comments_sum = 0
        for post in self.post_set.all(): # type: ignore[attr-defined]
            post_comments = post.comment_set.aggregate(total=Sum('rating'))['total'] or 0
            post_comments_sum += post_comments
        # Сумма рейтингов комментариев к постам автора
        self.rating_author = (post_sum * 3) + author_comments_sum + post_comments_sum
        self.save()

class Category(models.Model):
    name_category = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name_category

    def subscribers(self):
        """Возвращает QuerySet пользователей, подписанных на эту категорию."""
        return User.objects.filter(categorysubscription__category=self)

    def is_subscribed(self, user):
        """Проверяет, подписан ли конкретный user на эту категорию."""
        return CategorySubscription.objects.filter(user=user, category=self).exists()



class CategorySubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')  # Предотвращает дубли

    def __str__(self):
        return f"{self.user.username} → {self.category.name_category}"


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    TYPE_CHOICES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=10, choices=[('news', 'News'), ('article', 'Article')], default='news')  # Тип: статья или новость
    time_created = models.DateTimeField(auto_now_add=True)  # Авто-дата создания
    categories = models.ManyToManyField(Category, through='PostCategory', related_name='post', blank=False)
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.get_post_type_display()})" # type: ignore[attr-defined]

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        """Возвращает превью текста: первые 124 символа + многоточие.

           Returns:
                   str: Короткий текст превью. """

        return self.text[:124] + "..."

    def clean(self):
        super().clean()
        if self.pk:
            if not self.categories.exists():
                raise ValidationError({
                    'categories': 'Пост должен иметь хотя бы одну категорию.'
                })

    def get_absolute_url(self):

        return reverse('news:detail', args=[self.post_type, self.id])

    class Meta:
        permissions = [('can_add_news_post', 'Can add news post'),
            ("can_create_post", "Can create post"),
               ("can_edit_post", "Can edit post"),]




class PostCategory(models.Model):  # Промежуточная для ManyToMany
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.post.title} - {self.category.name_category}" # type: ignore[attr-defined]

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_set')  # Один ко многим с Post
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE)  # Один ко многим с User (любой может комментировать)
    text = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"Коммент от {self.comment_user.username} к {self.post.title}" # type: ignore[attr-defined]

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()