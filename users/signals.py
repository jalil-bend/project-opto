from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Professional

@receiver(post_save, sender=User)
def create_professional_profile(sender, instance, created, **kwargs):
    if created and instance.is_professional:
        Professional.objects.create(user=instance)
