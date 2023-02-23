from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Author, Genre, Story, Comment

from django.utils import timezone

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'stories_count')

class StoriesAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['title', 'author', 'genre', 'abstract', 'content']
        }),
        ('Date and Time', {
            'fields': ['date_published', 'date_last_updated']
        })
    ]
    
    readonly_fields = ('date_published', 'date_last_updated')
    list_display = ('title', 'author', 'get_genre')
    
    def save_model(self, request, obj, form, change):
        obj.date_last_updated = timezone.now()
        super().save_model(request, obj, form, change)
        
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'commenter', 'date_published')

# Register your models here.
admin.site.register(Author, UserAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Story, StoriesAdmin)
admin.site.register(Comment, CommentAdmin)