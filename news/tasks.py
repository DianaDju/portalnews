from django.core.mail import send_mail
from celery import shared_task
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Post, CategorySubscription


@shared_task
def send_new_post_email(post_id):
    post = Post.objects.get(id=post_id)
    categories = post.categories.all()
    subscriptions = CategorySubscription.objects.filter(category__in=categories)

    # Формируем полный URL
    full_url = f"{settings.SITE_BASE_URL}{post.get_absolute_url()}"

    for sub in subscriptions:
        message_html = render_to_string(
            'email/new_post_email.html',
            {'post': post, 'full_url': full_url}
        )
        send_mail(
            subject=f'Новая новость: {post.title}',
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.user.email],
            html_message=message_html,
            fail_silently=False,
        )
    return f'Done, sent {subscriptions.count()} emails'


@shared_task
def send_weekly_news():
    print("Weekly digest task started")

    now = timezone.now()
    week_ago = now - timezone.timedelta(days=7)

    # Обновлено поле на time_created
    posts = Post.objects.filter(time_created__gte=week_ago)

    if not posts.exists():
        return "No posts this week"

    subs = CategorySubscription.objects.select_related('user', 'category')

    user_posts = {}
    for sub in subs:
        user = sub.user
        user_cats_posts = posts.filter(categories=sub.category)
        if user_cats_posts.exists():
            user_posts.setdefault(user, set())
            user_posts[user].update(user_cats_posts)

    for user, posts_set in user_posts.items():
        posts_list = list(posts_set)


        for post in posts_list:
            post.full_url = f"{settings.SITE_BASE_URL}{post.get_absolute_url()}"

        html = render_to_string(
            'email/weekly_digest_email.html',
            {'posts': posts_list, 'user': user}
        )

        msg = EmailMultiAlternatives(
            subject='Еженедельная подборка новостей',
            body='Ваш почтовый клиент не поддерживает HTML.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=False)

    return f"Sent weekly digest to {len(user_posts)} users"




