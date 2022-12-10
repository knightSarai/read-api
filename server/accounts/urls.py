from django.urls import path 
from knox import views as knox_views

app_name = 'accounts'

urlpatterns = [
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall')
]


