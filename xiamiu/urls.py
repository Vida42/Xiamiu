from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    url(r'^artist/(?P<inputID>.*?)/$', views.showArtistPage, name='showArtistPage'),
    url(r'^album/(?P<inputID>.*?)/$', views.showAlbumPage, name='showAlbumPage'),
    url(r'^song/(?P<inputID>.*?)/$', views.showSongPage, name='showSongPage'),
    url(r'^genre/(?P<inputID>.*?)/$', views.showGenrePage, name='showGenrePage'),
    url(r'^search/$', views.search, name='search'),
    url(r'^search/artist/$', views.searchArtistByName, name='searchArtistByName'),
    url(r'^search/album/$', views.searchAlbumByName, name='searchAlbumByName'),
    url(r'^search/song/$', views.searchSongByName, name='searchSongByName')
]
