from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_schema/', views.new_schema, name='new_schema'),
    path('login/', views.log_in, name='log_in'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('new_schema/', views.new_schema, name='new_schema'),
    path('new_column/', views.new_column, name='new_column'),
    path('edit_schema/<int:id>/', views.edit_schema, name='edit_schema'),
    path('delete_schema/<int:id>/', views.delete_schema, name='delete_schema'),
    path('view_schema/<int:id>/', views.view_schema, name='view_schema'),
    path('generate_set/<int:id>/', views.generate_set, name='generate_set'),
    path('check_status/', views.check_status, name='check_status'),
    path('download/<filename>', views.download, name='download'),
]