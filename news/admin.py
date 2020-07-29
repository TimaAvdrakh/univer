from django.contrib import admin
from .models import News


class NewsModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'is_important']
    list_display_links = ['name']
    list_per_page = 20
    list_select_related = ['author']