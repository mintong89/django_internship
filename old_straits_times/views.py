from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse

from .models import Story, Genre, Author

import logging

# Create your views here.

def index(request):
    trending_stories = Story.objects.order_by('-views_total')[:5]
    template_name = 'old_straits_times/index.html'
    
    return render(request, template_name, {
        'trending_stories': trending_stories
    })
    
def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    template_name = 'old_straits_times/story.html'
    
    # add a view count for each user enter the page
    if story and story.author.pk != request.user.pk:
        story.views_total += 1
        story.save()
    
    return render(request, template_name, {
        'story': story
    })
    
def auth_login(request):
    template_name = 'old_straits_times/login.html'
    
    context = {
        'error_message': ''
    }
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('oldstimes:index'))
        else:
            context['error_message'] = 'Username or password incorrect.'
    
    return render(request, template_name, context)

def auth_logout(request):    
    logout(request)
    
    return HttpResponseRedirect(reverse('oldstimes:index'))

def profile(request, author_username):
    template_name = 'old_straits_times/profile.html'
    
    authorData = get_object_or_404(Author, username=author_username)
    
    return render(request, template_name, {
        "author": authorData
    })

def story_post(request):
    all_genre = Genre.objects.all()
    template_name = 'old_straits_times/story_post.html'
    
    if request.method == 'POST':
        title = request.POST.get('title')
        genre = request.POST.getlist('genre')
        abstract = request.POST.get('abstract')
        content = request.POST.get('content')
        date_published = timezone.now()
        date_last_updated = timezone.now()
        
        genre_pk = list(map(lambda x: Genre.objects.get(name=x), genre))
        
        new_story = Story(
            title=title,
            author=Author.objects.get(pk=request.user.pk),
            abstract=abstract,
            content=content,
            date_published=date_published,
            date_last_updated=date_last_updated
        )
        new_story.save()
        new_story.genre.set(genre_pk)
        return HttpResponseRedirect(reverse('oldstimes:story', kwargs={'story_id': new_story.pk}))
        
        
    
    return render(request, template_name, {
        'all_genre': all_genre
    })
    
def story_edit(request, story_id):
    current_story = get_object_or_404(Story, pk=story_id) 
    all_genre = Genre.objects.all()
    template_name = 'old_straits_times/story_edit.html'

    if request.method == 'POST':
        deleteStory = request.POST.get('delete_story')
        if deleteStory == 'true':
            current_story.delete()
            return HttpResponseRedirect(reverse('oldstimes:index'))
        
        title = request.POST.get('title')
        genre = request.POST.getlist('genre')
        abstract = request.POST.get('abstract')
        content = request.POST.get('content')
        date_last_updated = timezone.now()
        
        genre_pk = list(map(lambda x: Genre.objects.get(name=x), genre))
        
        current_story.title = title;
        current_story.abstract = abstract;
        current_story.content = content;
        current_story.date_last_updated = date_last_updated
        current_story.save()
        current_story.genre.set(genre_pk)
        return HttpResponseRedirect(reverse('oldstimes:story', kwargs={'story_id': current_story.pk}))
    
    

    return render(request, template_name, {
        'all_genre': all_genre,
        'current_story': current_story
    })
    
def settings_profile(request):
    template_name = 'old_straits_times/settings_profile.html'
    
    return render(request, template_name, {

    })