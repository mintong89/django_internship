import datetime
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.urls import reverse

from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

from .models import ProfileForm, Story, Genre, Author, Comment, StoryForm

from random import choice
import re
from django.db.models import Q

# Create your views here.
def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None,
    )

# -----------------------

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
    
def auth_login(request):
    template_name = 'old_straits_times/auth/login.html'
    
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('oldstimes:index'))
    
    context = {
        'success_message': '',
        'error_message': ''
    }
    
    if request.GET.get('m', '') == 'reg_success':
        context['success_message'] = 'Register sucessfully! Please login your account.'
    
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

def register(request):
    template_name = 'old_straits_times/auth/register.html'
    
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('oldstimes:index'))
    
    if request.method == 'POST':
        first_name:str = request.POST.get('first_name')
        last_name:str = request.POST.get('last_name')
        username:str = request.POST.get('username')
        email:str = request.POST.get('email')
        password:str = request.POST.get('password')
        confirmation_password:str = request.POST.get('confirmation_password')
        
        # check username
        if not re.match(r'[a-zA-Z0-9@.+-_]{8,20}', username):
            return render(request, template_name, {
                'error_message': "The username does not meet criteria!"
            })
            
        if Author.objects.filter(username=username).exists():
            return render(request, template_name, {
                'error_message': "The username has been used! Try another username."
            })
        
        # check email address
        try:
            validate_email(email)
        except:
            return render(request, template_name, {
                'error_message': "Invalid email address!"
            })
            
        if Author.objects.filter(email=email).exists():
            return render(request, template_name, {
                'error_message': "The email address has been used!"
            })
        
        # check password
        try:
            validate_password(password)
        except:
            return render(request, template_name, {
                'error_message': "Invalid password!"
            })
        
        # check confirmation password
        if confirmation_password != password:
            return render(request, template_name, {
                'error_message': "Password not match!"
            })
            
        new_author = Author.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email
        )
        new_author.set_password(password)
        new_author.save()
        
        return HttpResponseRedirect('%s?m=reg_success' % reverse('oldstimes:auth_login'))
        
    return render(request, template_name, {})

def profile(request, author_username):
    template_name = 'old_straits_times/profile.html'
    
    authorData = get_object_or_404(Author, username=author_username)
    
    return render(request, template_name, {
        "author": authorData
    })

def story_post(request):
    all_genre = Genre.objects.all()
    template_name = 'old_straits_times/story/post.html'
    
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.cleaned_data['author'] = Author.objects.get(pk=request.user.pk)
            form.cleaned_data['date_published'] = timezone.now()
            form.cleaned_data['date_last_updated'] = timezone.now()

            genre = request.POST.getlist('genre_raw')
            genre_pk = list(map(lambda x: Genre.objects.get(name=x), genre))
            
            new_story = form.save()
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
        title = request.POST.get('title')
        genre = request.POST.getlist('genre')
        abstract = request.POST.get('abstract')
        content = request.POST.get('content')
        is_private = request.POST.get('is_private')
        date_last_updated = timezone.now()
        
        genre_pk = list(map(lambda x: Genre.objects.get(name=x), genre))
        
        current_story.title = title;
        current_story.abstract = abstract;
        current_story.content = content;
        current_story.date_last_updated = date_last_updated
        current_story.is_private = not not is_private
        current_story.save()
        current_story.genre.set(genre_pk)
        return HttpResponseRedirect(reverse('oldstimes:story', kwargs={'story_id': current_story.pk}))

    return render(request, template_name, {
        'all_genre': all_genre,
        'current_story': current_story
    })

def settings_profile(request):
    template_name = 'old_straits_times/settings/profile.html'
    author = get_object_or_404(Author, pk=request.user.pk)
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        new_password_confirmation = request.POST.get('new_password_confirmation')
        
        if current_password and new_password and new_password_confirmation:
            if new_password != new_password_confirmation:
                return render(request, template_name, {
                    "author": author,
                    'error_message': "New password is not same as confirmation!"
                })   
            
            if author.check_password(new_password):
                author.set_password(new_password)
            else:
                return render(request, template_name, {
                    "author": author,
                    'error_message': "Current password is not correct!"
                })       
        
        form = ProfileForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            avatar_existing = request.POST.get('avatar_existing')
            if avatar_existing != 'true':
                form.instance.avatar = None

            form.save()
        else:
            print(form.errors)
            
        return render(request, template_name, {
            "author": author,
            'success_message': "The profile has been successfully updated."
        })
        
    
    return render(request, template_name, {
        "author": author
    })
    
def settings_theme(request):
    template_name = 'old_straits_times/settings/theme.html'
    
    if request.method == 'POST':
        theme_color = request.POST.get('theme_color')
        request.COOKIES['theme_color'] = theme_color
        response = render(request, template_name, {})
        response.set_cookie('theme_color', theme_color)
        
        return response
    
    return render(request, template_name, {})

def settings_manage(request):
    template_name = 'old_straits_times/settings/manage.html'
    
    if request.method == 'POST':
        post_type = request.POST.get('post_type')
        pk = request.POST.get('pk')
        story = Story.objects.get(pk=pk)
        
        if pk:
            if post_type == 'private' or post_type == 'public':
                story.is_private = post_type == 'private'
                story.save() 
                
                return JsonResponse({
                    'message': f'Published or Privated Story {pk} from table!'
                })
            elif post_type == 'delete':
                story.delete()
                
                return JsonResponse({
                    'message': f'Deleted Story {pk} from table!'
                })
    
    stories = Story.objects.filter(author=request.user).order_by('-date_published')
    return render(request, template_name, {
        'stories': stories
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
