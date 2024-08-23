from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name= "index"),
    path('welcome',views.welcome,name= "welcome"),
    path('result',views.result,name= "result"),
    path('userid',views.userid,name= "userid"),
    path('login',views.login,name= "login"),
    path('userpage',views.userpage,name='userpage'),
    path('submit/', views.submit_exam, name='submit_exam'),
   
   
]

