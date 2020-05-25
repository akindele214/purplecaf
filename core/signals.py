from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import VoucherAccount

@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        VoucherAccount.objects.create(user=instance)


