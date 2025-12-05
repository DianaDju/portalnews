
from .models import PostCategory, CategorySubscription
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

@receiver(post_save, sender=PostCategory)
def send_email_on_new_post(sender, instance, created, **kwargs):
    if not created:
        return  # интересуют только новые связи

    post = instance.post
    category = instance.category

    subscribers_emails = set(
        CategorySubscription.objects.filter(category=category)
        .values_list('user__email', flat=True)
    )

    if not subscribers_emails:
        return

    for email in subscribers_emails:
        subject = f"Новый пост: {post.title}"
        text_content = f"Вышла новая статья: {post.title}"

        # Правильная генерация полного URL
        full_url = f"{settings.SITE_BASE_URL}{post.get_absolute_url()}"

        html_content = render_to_string(
            "email/new_post_email.html",
            {"post": post, "full_url": full_url}
        )

        msg = EmailMultiAlternatives(subject, text_content, 'dzhu.diana27@yandex.ru', [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Письмо отправлено: {email}")



User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance
    subject = "Добро пожаловать на PortalNews!"
    html_content = render_to_string(
        "email/welcome_email.html",
        {"user": user, "site_url": settings.SITE_BASE_URL}
    )
    text_content = f"Здравствуйте, {user.username}! Добро пожаловать на PortalNews! Сайт: {settings.SITE_BASE_URL}"

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print(f"Приветственное письмо отправлено: {user.email}")

