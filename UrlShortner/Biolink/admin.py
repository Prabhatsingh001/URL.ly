from django.contrib import admin
from .models import Link
# Register your models here.


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "user")
    list_filter = ("user",)
    search_fields = ("title", "url")
