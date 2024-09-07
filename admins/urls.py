from django.urls import path
from . import views
from .views import download_result

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
    path('export-pdf/<str:class_name>/', views.export_user_data_to_pdf, name='export_user_data_to_pdf'),
    path('delete/<str:pk>/', views.delete, name='delete'),
    path('profile',views.profile,name='profile'),
    path('result',views.result,name='result'),
    path('term/<str:pk>/',views.term,name='term'),
    path('subject/<str:pk>/',views.subject,name='subject'),
    path('status',views.status,name='status'),
    path('deleteuserid',views.deleteuserid,name='deleteuserid'),
    path('destroyexam',views.destroyexam,name='destroyexam'),
    path('releaseip',views.releaseip,name='releaseip'),
    path('ip/<str:user>/',views.ip,name='ip'),
    path('close-tab/',views.close_tab, name ='close_tab' ),
    path('api/user-status/', views.user_status_api, name='user_status_api'),
    path('generate/', views.generate_user_ids, name='generate_user_ids'),
    path('delete-gen/', views.delete_generated_ids, name='delete_generated_ids'),
    path('delete_user/<int:user_id>/',views.delete_user, name='delete_user'),
    path('download-result/<int:class_id>/<int:term_id>/<int:subject_id>/', download_result, name='download_result'),
]

 