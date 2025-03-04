from django.db import models


class User(models.Model):
    email = models.EmailField(max_length=30, unique=True)
    username = models.CharField(max_length=15)
    password = models.CharField(max_length=15)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)

    def __str__(self):
        return self.username
    

class Group_Chat(models.Model):
    group_name = models.CharField(max_length=15)
    group_image = models.ImageField(upload_to='group_image/')
    group_members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.group_name


class Message(models.Model):
    sender = models.CharField(max_length=20)
    reciever = models.CharField(max_length=20)
    message = models.TextField()
    time = models.DateTimeField()

    def __str__(self):
        return self.sender