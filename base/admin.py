from django.contrib import admin
from .models import User,Question, Answer,UserID ,Userprofile

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(UserID)
admin.site.register(Userprofile)

# Register your models here.
