from django.contrib import admin
from .models import *

# Register your models here.
model = [Room,Topic,Message,User]

for i in model:
    admin.site.register(i)
