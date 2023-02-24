from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.urls import reverse


from ..models import Story, Genre, Author, Comment, StoryForm


def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    template_name = 'old_straits_times/story/index.html'
    
    # add a view count for each user enter the page
    if story and story.author.pk != request.user.pk:
        story.views_total += 1
        story.save()
        
    if request.method == 'POST':
        post_type = request.POST.get('post_type')
        
        # if post type is to post comment
        if post_type == 'post_comment':
            content = request.POST.get('content')
            
            new_comment = Comment(
                story=story,
                commenter=request.user,
                content=content
            )
            new_comment.save()
            
        elif post_type == 'reply_comment':
            content = request.POST.get('content')
            reply_to = Comment.objects.get(pk=request.POST.get('reply_to'))
            
            new_reply = Comment(
                story=story,
                commenter=request.user,
                content=content,
                reply_to=reply_to
            )
            new_reply.save()
            
            return JsonResponse({'success': 'Replied Sucessfully'}, status=200)
        
        elif post_type == 'like_comment':
            comment_pk = request.POST.get('comment_pk')
            comment = Comment.objects.get(pk=comment_pk)
            
            author = Author.objects.get(pk=request.user.pk)
            if not comment.likes.filter(pk=request.user.pk).exists():
                comment.likes.add(author)
                if comment.dislikes.filter(pk=request.user.pk).exists():
                    comment.dislikes.remove(author)
            else:
                comment.likes.remove(author)
                
            return JsonResponse({
                'message': "Disliked Successfully",
                'like_count': comment.likes.count(),
                'dislike_count': comment.dislikes.count()
            })
            
        elif post_type == 'dislike_comment':
            comment_pk = request.POST.get('comment_pk')
            comment = Comment.objects.get(pk=comment_pk)
            
            author = Author.objects.get(pk=request.user.pk)
            if not comment.dislikes.filter(pk=request.user.pk).exists():
                comment.dislikes.add(author)
                if comment.likes.filter(pk=request.user.pk).exists():
                    comment.likes.remove(author)
            else:
                comment.dislikes.remove(author)
                
            return JsonResponse({
                'message': "Disliked Successfully",
                'like_count': comment.likes.count(),
                'dislike_count': comment.dislikes.count()
            })
    
    return render(request, template_name, {
        'story': story
    })
    
def story_post(request):
    all_genre = Genre.objects.all()
    template_name = 'old_straits_times/story/post.html'
    
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)

        if form.is_valid():
            new_story:Story = form.save(commit=False)

            new_story.author = Author.objects.get(pk=request.user.pk)
            new_story.date_published = timezone.now()
            new_story.date_last_updated = timezone.now()

            new_story.save()

            genre = request.POST.getlist('genre_raw')
            genre_pk = list(map(lambda x: Genre.objects.get(name=x), genre))
            new_story.genre.set(genre_pk)

            return HttpResponseRedirect(reverse('oldstimes:story', kwargs={'story_id': new_story.pk}))
    
    return render(request, template_name, {
        'all_genre': all_genre
    })
    
def story_edit(request, story_id):
    current_story = get_object_or_404(Story, pk=story_id) 
    all_genre = Genre.objects.all()
    template_name = 'old_straits_times/story/edit.html'

    if request.method == 'POST':
        # delete story
        deleteStory = request.POST.get('delete_story')
        if deleteStory == 'true':
            current_story.delete()
            return HttpResponseRedirect(reverse('oldstimes:index'))
        
        # edit story
        form = StoryForm(request.POST, request.FILES, instance=current_story)
        
        if form.is_valid():
            form.save(commit=False)

            current_story.author = Author.objects.get(pk=request.user.pk)
            current_story.date_last_updated = timezone.now()

            current_story.save()

            genre = request.POST.getlist('genre_raw')
            genre_pk = list(map(lambda x: Genre.objects.get(name=x), genre))
            current_story.genre.set(genre_pk)

            return HttpResponseRedirect(reverse('oldstimes:story', kwargs={'story_id': current_story.pk}))

    return render(request, template_name, {
        'all_genre': all_genre,
        'current_story': current_story
    })
