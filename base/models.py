from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save


# Create your models here.
class User(AbstractUser):
   school_name =models.CharField(max_length=500,null=True)
   recovery_code = models.CharField(max_length=100,null=True)

class Question(models.Model):
    text = models.TextField()
    diagram = models.ImageField(upload_to='questions/diagrams/', blank=True, null=True)  # Stores the path to the diagram image


    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
   



    




class UserID(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    generated_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.user.username


class Userprofile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
def save_user_model(sender ,instance,created,**kwargs):
    if created:
          Userprofile.objects.create(user=instance)
  

post_save.connect(save_user_model, sender=User )
