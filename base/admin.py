from django.contrib import admin
from .models import User,Question, Answer,UserID ,Userprofile ,Subject,Suffle,ExamSession ,Result

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(UserID)
admin.site.register(Userprofile)
admin.site.register(Subject)
admin.site.register(Suffle)
admin.site.register(ExamSession)
admin.site.register(Result)
# Register your models here.
