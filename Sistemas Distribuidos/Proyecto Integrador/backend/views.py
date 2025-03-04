from django.shortcuts import render
from .models import *


def get_chat_groups(email):
    chat_groups = Group_Chat.objects.all()
    return chat_groups

def get_messages(username):
    messages = Message.objects.all()
    return messages