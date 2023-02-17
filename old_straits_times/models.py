from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
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
    
