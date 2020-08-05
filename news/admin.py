from django.contrib import admin
from .models import News


class NewsModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_important']
    list_display_links = ['title']
    list_per_page = 20
    list_select_related = ['author']


admin.site.register(News, NewsModelAdmin)
