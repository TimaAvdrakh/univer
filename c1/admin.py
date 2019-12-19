from django.contrib import admin
from c1.models import C1Object, C1ObjectCompare


class C1CompareInline(admin.TabularInline):
    model = C1ObjectCompare
    extra = 3


@admin.register(C1Object)
class C1ObjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'model', 'is_related', 'is_active']
    inlines = [C1CompareInline, ]
