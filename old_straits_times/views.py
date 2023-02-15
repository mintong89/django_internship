from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import Story

# Create your views here.

def index(request):
    trending_stories = Story.objects.order_by('-views_in_week')[:5]
    template_name = 'old_straits_times/index.html'
    
    return render(request, template_name, {
        'trending_stories': trending_stories
    })
    
def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    template_name = 'old_straits_times/story.html'
    
    # add a view count for each user enter the page
    if story:
        story.views_total += 1
        story.save()
    
    return render(request, template_name, {
        'story': story
    })