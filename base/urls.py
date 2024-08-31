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
    path('complete/', views.complete, name='complete'), 
    path('save_selection/', views.save_selection, name='save_selection'), 
    path('get_selections/', views.get_selections, name='get_selectionsb'), 
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    

   
]

