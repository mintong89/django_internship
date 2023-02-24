import json
from random import choice
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q

from ..models import Story, Genre, Author

from .auth import *
from .settings import *
from .story import *


def index(request):
    template_name = 'old_straits_times/index.html'
    
    trending_stories = Story.objects.filter(is_private=False).order_by('-views_total')[:5]
    
    pks = Story.objects.values_list('pk', flat=True)
    random_pks = []
    if len(pks) <= 5:
        random_pks = pks
    else:
        while len(random_pks) != 5:
            random_pk = choice(pks)
            if random_pk not in random_pks:
                random_pks.append(random_pk)
    random_stories = Story.objects.filter(id__in=random_pks, is_private=False).order_by('date_last_updated')
    
    return render(request, template_name, {
        'trending_stories': trending_stories,
        'random_stories': random_stories
    })

def profile(request, author_username):
    template_name = 'old_straits_times/profile.html'
    
    authorData = get_object_or_404(Author, username=author_username)
    
    return render(request, template_name, {
        "author": authorData
    })

def category(request):
    template_name = 'old_straits_times/category.html'
    
    all_genre = Genre.objects.all()
    context = { 'all_genre': all_genre }
    
    selectedGenre = request.GET.getlist('genre')
    stories = Story.objects.filter(genre__in=selectedGenre, is_private=False).distinct() if selectedGenre else Story.objects.filter(is_private=False)
    context['stories'] = stories[:20]
    
    return render(request, template_name, context)

def search(request):
    def simplified_story(story: Story):
        return {
            'pk': story.pk,
            'title': story.title,
            'genre': story.get_genre(),
            'author': story.author.username
        }

    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        search_result = list(map(
            simplified_story, 
            Story.objects.filter(
                (Q(title__icontains=search_query) |
                Q(genre__name__icontains=search_query)) &
                Q(is_private=False)
                ).distinct()[:8],
            ))
        
        return JsonResponse({
            "result": json.dumps(search_result)
        }, safe=False)

    template_name = 'old_straits_times/index.html'
    return render(request, template_name, {})
