from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver



class User(AbstractUser):
    school_name = models.CharField(max_length=500, null=True,blank=True)
    recovery_code = models.CharField(max_length=100, null=True)

class Name_School(models.Model):
    school = models.CharField(max_length=345)

    def __str__(self):
        return self.school

@receiver(post_save, sender=User)
def save_user_model(sender, instance, created, **kwargs):
    if created and instance.is_staff and instance.school_name:
        # Create the Name_School object if it doesn't already exist
        Name_School.objects.get_or_create(school=instance.school_name)


class TermOrSemester(models.Model):
    TERM_CHOICES = [
        ('first_term', 'First Term'),
        ('second_term', 'Second Term'),
        ('third_term', 'Third Term'),
        ('first_semester', 'First Semester'),
        ('second_semester', 'Second Semester'),
    ]
    
    name = models.CharField(max_length=20, choices=TERM_CHOICES)

    def __str__(self):
        return self.get_name_display()

from django.db import models

class ClassOrLevel(models.Model):
    CLASS_LEVEL_CHOICES = [
        ('jss1', 'JSS 1'),
        ('jss2', 'JSS 2'),
        ('jss3', 'JSS 3'),
        ('sss1', 'SSS 1'),
        ('sss2', 'SSS 2'),
        ('sss3', 'SSS 3'),
        ('cbt', 'CBT'),
        ('level_100', 'Level 100'),
        ('level_200', 'Level 200'),
        ('level_300', 'Level 300'),
        ('level_400', 'Level 400'),
    ]
    
    name = models.CharField(max_length=20, choices=CLASS_LEVEL_CHOICES)

    def __str__(self):
        return self.get_name_display()


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    text = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,null=True)
    term_or_semester = models.ForeignKey(TermOrSemester, on_delete=models.CASCADE, null=True, blank=True)
    class_or_level = models.ForeignKey(ClassOrLevel, on_delete=models.CASCADE, null=True, blank=True)
    diagram = models.ImageField(upload_to='questions/diagrams/', null=True, blank=True)

    def __str__(self):
        return self.text[:50] 

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
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    exam_start_time = models.DateTimeField(default=timezone.now)
    exam_duration = models.CharField(max_length=8, default='01:00:00')  # Format hh:mm:ss
    completed = models.BooleanField(default=False)
    shuffle_order = models.PositiveIntegerField(null=True) 
    submit = models.BooleanField(default=False) # Existing field for shuffle order
 
    def __str__(self):
        return f'{self.subject.name} - {self.question.text[:50]}'
    def get_questions(self):
        
        return Question.objects.filter(examsession=self).order_by('shuffle_order')



class UserExamSessionx(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)  # Track subject separately
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, null=True)
    start_time = models.DateTimeField(default=timezone.now)  # When the user starts the exam

    class Meta:
        unique_together = ('user', 'subject')  # Ensure unique sessions per user per subject

    def __str__(self):
        return f"UserExamSession - User: {self.user.username}, Subject: {self.subject.name}"

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
    

class User_result(models.Model):
    userid = models.ForeignKey(UserID, on_delete=models.CASCADE)
    correct_answers = models.CharField(max_length=255, null=True,blank=True)
    total_questions =  models.CharField(max_length=255, null=True,blank=True)
    

    def __str__(self):
        return self.userid.user.username
def save_user_model(sender ,instance,created,**kwargs):
    if created:
          User_result.objects.create(userid=instance)
  

post_save.connect(save_user_model, sender=UserID ) 


class UserSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # If using Django's user model
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

class Loding(models.Model):
    user =  models.ForeignKey(User,on_delete=models.CASCADE , null= True)
    login = models.BooleanField(default=False)


  