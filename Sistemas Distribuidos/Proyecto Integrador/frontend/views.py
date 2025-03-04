from django.shortcuts import render, redirect
from backend.models import *
from backend.views import *
from .forms import *

# Create your views here.
def index(request):
    if request.method == "POST":
        user = UserForm(data=request.POST)
        if user.is_valid():
            user = user.save()
            return redirect('chats')
    else:
        userForm = UserForm()
    return render(request, 'index.html',{'UserForm':UserForm})

def login(request):
    return render(request, 'login.html', {'LoginForm':LoginForm})

def reset(request):
    return render(request, 'reset.html', {'ResetPForm': ResetPForm})


def chats(request):
    chat_groups = get_chat_groups('raquezad.dev@gmail')
    messages = get_messages('SpicyNoodles')
    return render(request, 'chats.html', {'chat_groups':chat_groups,'messages':messages})