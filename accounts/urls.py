from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register_user/', views.Register_User, name='register'),
    path('login_user/', views.Login_User, name='login'),
    path('logout_user/', views.Logout_User, name='logout'),
    path('forgot_password/', views.Forgot_Password, name='forgot_password'),


    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),

]
