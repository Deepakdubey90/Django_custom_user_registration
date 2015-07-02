import uuid
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template import RequestContext
from django.core.mail import send_mail
import hashlib, datetime, random
from django.utils import timezone
from django.core.context_processors import csrf
#from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationForm
from .models import (MyUserProfile,
                     MyUser)


def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)

def auth_view(request):
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(email=email, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/accounts/loggedin/')
    else:
        return HttpResponseRedirect('/accounts/invalid/')

def confirm_registration(request, activation_key):
    #check if user is already logged in and if he is redirect him to some other url, e.g. home
    if request.user.is_authenticated():
        HttpResponseRedirect('/home/')

    # check if there is UserProfile which matches the activation key (if not then display 404)
    user_profile = get_object_or_404(MyUserProfile, activation_key=activation_key)

    #check if the activation key has expired, if it hase then render confirm_expired.html
    if user_profile.key_expires < timezone.now():
        return render_to_response('user_profile/confirm_expired.html')
    #if the key hasn't expired save user and set him as active and render some template to confirm activation
    user = user_profile.user
    user.is_active = True
    user.save()
    return render_to_response('user_profile/confirm.html')


def loggedin(request):
    return render_to_respo3nse('loggedin.html',
                              {'full_name':request.user.username})

def invalid_login(request):
    return render_to_response('invalid_login.html')

def logout(request):
    auth.logout(request)
    return render_to_response('logout.html')

def register_user(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        args['form'] = form
        if form.is_valid():
            form.save();
            print(form.cleaned_data, "form_cleaned data")
            #username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            #Generate activation key
            #salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            #activation_key = hashlib.sha1(salt+email).hexdigest()
            activation_key = str(uuid.uuid4())
            key_expires = datetime.datetime.today() + datetime.timedelta(2)

            #Get user by email
            user=MyUser.objects.get(email=email)

            # Create and save user profile
            new_profile = MyUserProfile(user=user, activation_key=activation_key,
                                        key_expires=key_expires)
            new_profile.save()

            # Send email with activation key
            email_subject = 'Account confirmation'
            email_body = "Hey %s, thanks for signing up. To activate your account, click this link within \
            48hours http://127.0.0.1:8000/confirm/%s" % (email, activation_key)

            send_mail(email_subject, email_body, 'deepakdubey597@gmail.com',
                [email], fail_silently=False)

            return HttpResponseRedirect('/accounts/register_success/')
    else:
        args['form'] = UserCreationForm()
        return render_to_response('register.html', args, context_instance=RequestContext(request))

def register_success(request):
    return render_to_response('register_success.html');
