from django.contrib import admin
from .models import User,Question, Answer

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Answer)

# Register your models here.
