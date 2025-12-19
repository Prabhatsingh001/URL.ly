from django.contrib import admin
from .models import BlogPost, PostLikes, Comment

# Register your models here.

admin.site.register(BlogPost)
admin.site.register(PostLikes)
admin.site.register(Comment)
