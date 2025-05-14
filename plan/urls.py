from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('email/', views.email, name="email"),
    path('logout/', views.logout_user, name='logout'),
    path('viewuser/<str:pk>/', views.view_user, name="viewuser"),
    path('success/', views.success, name="success"),
    path('bill/', views.bill, name="bill"),
    path('plans/', views.plans, name="plans"),
    path('createplan/', views.create_plan, name="createplan"),
    path('deletplan/<int:pk>/', views.delete_plan, name="deleteplan"),
    path('users/', views.users, name="users"),
    path('createuser/', views.create_user, name="createuser"),
    path('deletuser/<int:pk>/', views.delete_user, name="deleteuser"),
    path('blank/', views.blank, name='blank'),
    path('media-inline/<path:path>', views.inline_pdf, name='inline_pdf'),
    path('login', views.login_page, name="login"),
    path('reports/', views.reports, name="reports"),
    path('generate-report/', views.generate_report, name="generate_report"),
    path('analytics/', views.analytics, name='analytics'),
    path('<int:pk>/', views.update_plan, name="updateplan"),
    path('<str:pk>/', views.edit_user, name="updateuser"),
]