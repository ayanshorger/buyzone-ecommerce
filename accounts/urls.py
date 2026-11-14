from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('addresses/', views.address_book, name='address_book'),
    path('addresses/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:pk>/default/', views.address_set_default, name='address_set_default'),
]
