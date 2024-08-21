from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save



class User(AbstractUser):
   school_name =models.CharField(max_length=500,null=True)
   recovery_code = models.CharField(max_length=100,null=True)

class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    text = models.TextField()
    diagram = models.ImageField(upload_to='questions/diagrams/', blank=True, null=True) 
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions',null=True)



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
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)
    number_of_questions = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username
def save_user_model(sender ,instance,created,**kwargs):
    if created:
          Userprofile.objects.create(user=instance)
  

post_save.connect(save_user_model, sender=User )

class Suffle(models.Model):
  
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)
    number_of_questions = models.IntegerField(null=True, blank=True)
    time_limit = models.IntegerField(null=True, blank=True)  # Sto

    def __str__(self):
        return f"{self.subject.name} - {self.number_of_questions} questions"
from django.utils import timezone

class ExamSession(models.Model):
    session_id = models.CharField(max_length=255, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    exam_start_time = models.DateTimeField(default=timezone.now)
    exam_duration = models.CharField(max_length=8, default='01:00:00')  # Format hh:mm:ss
    completed = models.BooleanField(default=False)
    shuffle_order = models.PositiveIntegerField(null=True)  # Existing field for shuffle order
 
    def __str__(self):
        return f'{self.subject.name} - {self.question.text[:50]}'
    def get_questions(self):
        
        return Question.objects.filter(examsession=self).order_by('shuffle_order')
    
class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)
    date_taken = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} - {self.subject.name} - {self.score}'