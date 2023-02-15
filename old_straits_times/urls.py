from django.urls import path
from . import views

app_name = 'oldstimes'
urlpatterns = [
    path('', views.index, name='index'),
    path('story/<int:story_id>', views.story, name='story'),
    path('auth/login', views.auth_login, name='auth_login'),
    path('auth/logout', views.auth_logout, name='auth_logout')
]