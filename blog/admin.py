"""Django Admin Modules"""

from django.contrib import admin

from .models import AboutUs, Category, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "content")
    search_fields = ("title", "content")
    list_filter = ("category", "created_at")


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(AboutUs)
