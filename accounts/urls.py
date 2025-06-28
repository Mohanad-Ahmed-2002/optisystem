from django.urls import path
from . import views
urlpatterns = [
    
    path('add-employee/', views.add_employee, name='add_employee'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('choose-plan/', views.choose_plan, name='choose_plan'),
    path('signup/<int:plan_id>/', views.signup_with_plan, name='signup_with_plan'),
    path('waiting-approval/', views.waiting_approval, name='waiting_approval'),
    path('pending-approvals/', views.pending_approvals, name='pending_approvals'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('platform-admin/', views.platform_admin_dashboard, name='platform_admin_dashboard'),
    path('activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('admin/delete-user/<int:user_id>/', views.superuser_delete_user, name='superuser_delete_user'),
    path('redirect/', views.custom_redirect_view, name='custom_redirect'),

]
