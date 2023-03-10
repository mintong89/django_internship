from django.urls import path
from . import views

app_name = 'oldstimes'
urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<slug:author_username>', views.profile, name='profile'),
    path('category', views.category, name='category'),
    path('search', views.search, name='search'),

    path('story/<int:story_id>', views.story, name='story'),
    path('story/<int:story_id>/edit', views.story_edit, name='story_edit'),
    path('post', views.story_post, name='story_post'),

    path('auth/login', views.auth_login, name='auth_login'),
    path('auth/logout', views.auth_logout, name='auth_logout'),
    path('register', views.auth_register, name='register'),

    path('settings/profile', views.settings_profile, name='settings_profile'),
    path('settings/manage', views.settings_manage, name='settings_manage'),
    path('settings/theme', views.settings_theme, name='settings_theme')
]