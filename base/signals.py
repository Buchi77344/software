from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
from .models import Userprofile ,Name_School,User_result,UserID # Adjust import based on your actual UserProfile model

@receiver(post_save, sender=User)
def save_user_model(sender, instance, created, **kwargs):
    if created and instance.is_staff and instance.school_name:
        # Create the Name_School object if it doesn't already exist
        Name_School.objects.get_or_create(school=instance.school_name)

@receiver(post_save, sender=User)
def save_user_model(sender ,instance,created,**kwargs):
    if created:
          Userprofile.objects.create(user=instance)
  

post_save.connect(save_user_model, sender=User )

@receiver(post_save, sender=User)
def save_user_model(sender ,instance,created,**kwargs):
    if created:
          User_result.objects.create(userid=instance)
  

post_save.connect(save_user_model, sender=UserID )
