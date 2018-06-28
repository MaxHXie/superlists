from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import auth, messages
from accounts.models import Token, User

# Create your views here.
def send_login_email(request):
    email = request.POST.get('email')
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse('login') + '?token=' + str(token.uid)
    )
    message_body = f'Use this link to log in:\n\n{url}'
    send_mail(
         'Your login link for Superlists',
         'Use this link to log in: ' + url,
         'noreply@superlists',
         [email]
    )
    messages.success(
        request,
        "Check your email, we have sent you a link you can use to log in."
    )
    return redirect('/')

'''
request.build_absolute_uri deserves a mention - it is one way to build a "full"
URL, including the domain name and the http(s) part, in Django. There are other ways,
but they usually involve getting into the "sites" framework, and that gets overcomplicated
pretty quickly. You can find lots more discussion on this if you are curious
by doing a bit of googling.
'''

def login(request):
    user = auth.authenticate(uid=request.GET.get('token'))
    if user:
        auth.login(request, user)
    return redirect('/')
