from django.contrib import admin

# Register your models here.
from .models import Movies, Critics

admin.site.register(Movies)
admin.site.register(Critics)