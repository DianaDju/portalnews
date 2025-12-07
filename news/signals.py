from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from .tasks import send_new_post_email

@receiver(post_save, sender=Post)
def send_email_after_post(sender, instance, created, **kwargs):
    if created:
        send_new_post_email.delay(instance.id)








