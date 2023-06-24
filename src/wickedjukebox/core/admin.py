from django.contrib import admin

from .models import Album, Artist, Channel, Playlist, Queue, Song, User

admin.site.register(User)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Song)
admin.site.register(Channel)
admin.site.register(Playlist)
admin.site.register(Queue)
