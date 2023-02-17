from django.urls import path
from . import views

app_name = 'oldstimes'
urlpatterns = [
    path('', views.index, name='index'),
    path('story/<int:story_id>', views.story, name='story'),
    path('story/<int:story_id>/edit', views.story_edit, name='story_edit'),
    path('auth/login', views.auth_login, name='auth_login'),
    path('auth/logout', views.auth_logout, name='auth_logout'),
    path('register', views.register, name='register'),
    path('profile/<slug:author_username>', views.profile, name='profile'),
    path('post', views.story_post, name='story_post'),
    path('settings/profile', views.settings_profile, name='settings_profile')
]