import datetime
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from ..models import ProfileForm, Story, Author

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
    