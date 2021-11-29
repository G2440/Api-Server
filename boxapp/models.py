from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
import uuid

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=500)
    username = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return str(self.username)

    class Meta:
        ordering = ['created']

class Store(models.Model):
    name = models.CharField(max_length=200,default="Main")
    current_total_area = models.IntegerField(default=0)
    total_boxes = models.IntegerField(default=0)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return self.name

class Box(models.Model):
    creator = models.ForeignKey(Profile,on_delete=models.SET_NULL,null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(default=datetime.now)
    length = models.IntegerField()
    breadth = models.IntegerField()
    height = models.IntegerField()
    area = models.IntegerField()
    volume = models.IntegerField()
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    class Meta:
        ordering = ['-created']