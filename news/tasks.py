from django.utils import timezone
from datetime import timedelta
from .models import Post, CategorySubscription
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def weekly_digest():
    print(">>> APSCHEDULER: weekly_digest STARTED")
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    for subscription in CategorySubscription.objects.all():
        category = subscription.category
        user = subscription.user

        posts = Post.objects.filter(
            categories__id=category.id,
            time_created__gte=week_ago
        ).distinct().order_by('-time_created')

        if not posts:
            continue

        subject = f"Список новых статей за неделю в категории {category.name_category}"


        html_content = render_to_string(
            "email/weekly_digest_email.html",
            {
                "user": user,
                "category": category,
                "posts": posts,
                "site_url": settings.SITE_BASE_URL
            }
        )


        text_content = "\n".join([f"{post.title}: {settings.SITE_BASE_URL}{post.get_absolute_url()}" for post in posts])

        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Письмо отправлено: {user.email}")

    print(f">>> Current time: {now}")

