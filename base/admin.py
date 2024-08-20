from django.contrib import admin
from .models import User,Question, Answer,UserID ,Userprofile ,Subject,Suffle,ExamSession

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(UserID)
admin.site.register(Userprofile)
admin.site.register(Subject)
admin.site.register(Suffle)
admin.site.register(ExamSession)
# Register your models here.
