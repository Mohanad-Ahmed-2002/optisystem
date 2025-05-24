from django.urls import path
from . import views
urlpatterns = [
    
    path('add-employee/', views.add_employee, name='add_employee'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    
]
