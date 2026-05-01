from django.urls import path
from . import views

urlpatterns = [
    path('',views.home_page, name='home'),
    path('register/', views.registration, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('profile/', views.profile_page, name='profile'),
    path('deposit/', views.deposit_page, name='deposit'),
    path('withdraw/', views.withdraw_page, name='withdraw'),
    path('transaction/', views.transaction_history, name='transaction'),
    path('transfer/', views.transfer_money, name='transfer'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]