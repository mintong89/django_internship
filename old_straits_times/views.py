import datetime
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.forms import ModelForm

from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

from .models import Story, Genre, Author, Comment

from random import choice
import re
from django.db.models import Q

# Create your views here.

# batching set value for posting
def set_post_value(req, obj, value: str, list_obj: (object | bool) = False, allow_empty = True):
    if list_obj:
        result = req.POST.getlist(value)
    else:
        result = req.POST.get(value)
    
    if result and not allow_empty:
        return False
    
    if list_obj:
        result = req.POST.getlist(value)
        return list(map(lambda x: list_obj.objects.get(name=x), result))
    else:
        setattr(obj, value, result)
    
    return True

def set_post_value_batch(req, obj, values: list[str]):
    [set_post_value(req, obj, value) for value in values]

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
    
    trending_stories = Story.objects.order_by('-views_total')[:5]
    
    pks = Story.objects.values_list('pk', flat=True)
    random_pks = []
    if len(pks) <= 5:
        random_pks = pks
    else:
        while len(random_pks) != 5:
            random_pk = choice(pks)
            if random_pk not in random_pks:
                random_pks.append(random_pk)
    random_stories = Story.objects.filter(id__in=random_pks).order_by('date_last_updated')
    
    return render(request, template_name, {
        'trending_stories': trending_stories,
        'random_stories': random_stories
    })
    
def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    template_name = 'old_straits_times/story.html'
    
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
    template_name = 'old_straits_times/login.html'
    
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
    template_name = 'old_straits_times/register.html'
    
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
    
class ProfileForm(ModelForm):
    class Meta:
        model = Author
        fields = [
            'email',
            'avatar',
            'bio',
            'first_name',
            'last_name',
            'country',
            'social1',
            'social2',
            'social3',
            'social4'
        ]

def settings_profile(request):
    template_name = 'old_straits_times/settings_profile.html'
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
            avatar_value = request.FILES.get('avatar')
            if not avatar_value:
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
    template_name = 'old_straits_times/settings_theme.html'
    
    if request.method == 'POST':
        response = render(request, template_name, {})
        response.set_cookie('theme_color', request.POST.get('theme_color'))
        
        return response
    
    return render(request, template_name, {})
    
def category(request):
    template_name = 'old_straits_times/category.html'
    
    all_genre = Genre.objects.all()
    context = { 'all_genre': all_genre }
    
    selectedGenre = request.GET.getlist('genre')
    stories = Story.objects.filter(genre__in=selectedGenre).distinct() if selectedGenre else Story.objects.all()
    context['stories'] = stories[:20]
    
    return render(request, template_name, context)

def simplified_story(story: Story):
    return {
        'pk': story.pk,
        'genre': story.get_genre(),
        'author': story.author.username
    }

def search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        search_result = list(map(
            simplified_story, 
            Story.objects.filter(Q(title__icontains=search_query) | Q(genre__name__icontains=search_query)).distinct()[:8]
            ))
        
        return JsonResponse({
            "result": json.dumps(search_result)
        }, safe=False)

    template_name = 'old_straits_times/index.html'
    return render(request, template_name, {})
