from django.contrib import admin

# Register your models here.
from .models import Folder, Book, Page, SkipRule

admin.site.register(Folder)
admin.site.register(Book)
admin.site.register(Page)
admin.site.register(SkipRule)
