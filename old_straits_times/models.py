from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.db.models import Q
from ckeditor.fields import RichTextField

import re

# Create your models here.
class Author(AbstractUser):
    bio = RichTextField()
    country = models.CharField(max_length=60, default="")
    
    social1 = models.CharField(max_length=120, default="")
    social2 = models.CharField(max_length=120, default="")
    social3 = models.CharField(max_length=120, default="")
    social4 = models.CharField(max_length=120, default="")
    
    def stories(self):
        return Story.objects.filter(author=self.pk).order_by('-date_published')
    
    def stories_count(self):
        return self.stories().count()
    
    def total_views(self): 
        return sum([story.views_total for story in self.stories()])
    
class Genre(models.Model):
    name = models.CharField(max_length=30)
    
    def stories_count(self):
        return Story.objects.filter(genre=self.pk).count()
    
    def __str__(self) -> str:
        return self.name

class Story(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.ManyToManyField(Genre)
    abstract = models.TextField(max_length=250, blank=True,
                                   validators=[MaxLengthValidator(250)])
    date_published = models.DateTimeField('date published', auto_now_add=True)
    date_last_updated = models.DateTimeField('date last updated')
    views_in_week = models.IntegerField(default=0)
    views_total = models.IntegerField(default=0)
    content = RichTextField()
    
    def comments(self):
        return Comment.objects.filter(story=self.pk, reply_to=None).order_by('-date_published')
    
    def get_views_total(self):
        return f'{self.views_total:3}'
    
    def get_word_count(self):
        return len(re.sub(r'<.*?>||&.*?;||^\n', '', self.content).strip())
    
    def get_reading_time_taken(self):
        return round(self.get_word_count() / 200, 2)
    
    def get_genre(self):
        return ", ".join([s.name for s in self.genre.all()])
    get_genre.short_description = 'Genre'
    
    def __str__(self) -> str:
        return self.title
    
class Comment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    commenter = models.ForeignKey(Author, null=True, on_delete=models.SET_NULL)
    reply_to = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    date_published = models.DateTimeField('date published', auto_now_add=True)
    edited = models.BooleanField(default=False)
    likes = models.ManyToManyField(Author, blank=True, related_name='likeses')
    dislikes = models.ManyToManyField(Author, blank=True, related_name='dislikeses')
    
    def replies(self):
        return Comment.objects.filter(reply_to=self)