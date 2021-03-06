from django.contrib import admin

# Register your models here.
from .models import Artist, Album, Song, Genre

# admin.site.register(User)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Song)
admin.site.register(Genre)
# admin.site.register(Favorite)
