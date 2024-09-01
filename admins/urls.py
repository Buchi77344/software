from django.urls import path
from . import views

app_name ='admins'

urlpatterns = [
    path('dashboard',views.dashboard , name= "dashboard"),
    path('signup',views.signup,name= "signup"),
    path('login',views.login,name= "login"),
    path('userid',views.userid,name= "userid"),
    path('user',views.user,name='user'),
    path('launch/<int:pk>/',views.launch,name='launch'),
    path('upload',views.upload,name= "upload"),
    path('logout',views.logout,name= "logout"),
    path('question_list',views.question_list,name= "question_list"),
    path('search',views.search,name='search'),
    path('question',views.question,name='question'),
    path('export-to-excel/',views.export_user_data_to_pdf, name='export_user_data_to_pdf'),
    path('delete/<str:pk>/', views.delete, name='delete'),
    path('profile',views.profile,name='profile'),
    path('result',views.result,name='result'),
    path('term/<str:pk>/',views.term,name='term'),
    path('subject/<str:pk>/',views.subject,name='subject'),
    path('status',views.status,name='status'),
    path('deleteuserid',views.deleteuserid,name='deleteuserid'),
    path('destroyexam',views.destroyexam,name='destroyexam'),
]
