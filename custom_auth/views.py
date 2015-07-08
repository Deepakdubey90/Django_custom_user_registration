import uuid
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
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
from twilio.rest import TwilioRestClient
from .forms import UserCreationForm
from .models import (MyUserProfile,
		     MyUser)


def loggedin(request):
    return render_to_respo3nse('loggedin.html',
			       {'full_name':request.user.userProfilename})

    #def home(request):
    #   return render_to_response('invalid_login.html')

def invalid_login(request):
    return render_to_response('invalid_login.html')

def auth_login(request):
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
	#form = UserCreationForm(request.POST)
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/accounts/loggedin/')
        else:
            return HttpResponseRedirect('/accounts/invalid/')
    else:
        form = UserCreationForm()
    return render_to_response('login.html', c)


    #def auth_view(request):
    #   print("auth_view called", request.post)

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
            userprofilename = form.cleaned_data['userprofilename']
            email = form.cleaned_data['email']
            contact_no = form.cleaned_data['contact_no']
            #Generate activation key
            activation_key = str(uuid.uuid4())
            key_expires = datetime.datetime.today() + datetime.timedelta(2)

            #Get user by email
            user=MyUser.objects.get(email=email)

            # Create and save user profile
            new_profile = MyUserProfile(user=user, activation_key=activation_key,
					key_expires=key_expires)
            new_profile.save()
            # send message useing twilio .com
            # Your Account Sid and Auth Token from twilio.com/user/account
            account_sid = "AC051c7b4e1e9044d87bd71d16cfa85e0f"
            auth_token  = "512a9ac72a7302760d6be0cdaf3105db"
            client = TwilioRestClient(account_sid, auth_token)
            print("value of client is", client)
            # iDrQl7b9cyBXDt18AKugZOjGrCxLmN+MY0qsVXvK// emergency code
            message = client.messages.create(
                body="Hello"+userprofilename+", You have been registered successfully.",
                to="+19095701688",    # Replace with your phone number
                from_="+18326328758") # Replace with your Twilio number
            
            call = client.calls.create(to="+19095701688",
                                       from_="+18326328758",
                                       url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient")
            print (message.sid)
	    # Send email with activation key
            email_subject = 'Account confirmation'
            email_body = "Hey %s, thanks for signing up. To activate your account, click this link within \
            48hours http://127.0.0.1:8000/confirm/activation_key/%s" % (userprofilename, activation_key)
            send_mail(email_subject, email_body, 'deepakdubey597@gmail.com',
                    [email], fail_silently=False)
            
            return HttpResponseRedirect('/accounts/register_success/')
    else:
        args['form'] = UserCreationForm()
        return render_to_response('register.html', args, context_instance=RequestContext(request))

def register_success(request):
    return render_to_response('register_success.html');
