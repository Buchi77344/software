from django.urls import path
from . import views

app_name ='admins'

urlpatterns = [
    path('dashboard',views.dashboard , name= "dashboard"),
    path('signup',views.signup,name= "signup"),
    path('login',views.login,name= "login"),
    path('userid',views.userid,name= "userid"),
    path('user',views.user,name='user'),
    path('launch',views.launch,name='launch'),
    path('upload',views.upload,name= "upload"),
    path('logout',views.logout,name= "logout"),
    path('question_list',views.question_list,name= "question_list"),
]
