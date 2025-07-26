from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 👈 add this line for home page
    path('predict/', views.predict_image, name='predict'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
]