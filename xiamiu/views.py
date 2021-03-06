from django.shortcuts import render
from django.http import HttpResponse
from .models import Artist, Album, Song, Genre
from django.shortcuts import render
from django.db import connection


# Create your views here.
def index(request):
    return render(request, 'home.html')


def showArtistPage(request, inputID):
    artistRes = []
    with connection.cursor() as cursor:
        cursor.callproc('show_artist_pic', (inputID,))
        each = cursor.fetchone()
        content = {'picAddress': each[0]}
        artistRes.append(content)
    with connection.cursor() as cursor:
        cursor.callproc('show_artist_info', (inputID,))
        each = cursor.fetchone()
        content = {'artistInfo': each[0]}
        artistRes.append(content)
    with connection.cursor() as cursor:
        cursor.callproc('show_artist_details', (inputID,))
        tmp = []
        for each in cursor.fetchall():
            content = {'artistName': each[0],
                       'artistReign': each[2],
                       'genreID': each[3],
                       'genreName': each[4]}
            tmp.append(content)
        artistRes.append(tmp)
    with connection.cursor() as cursor:
        cursor.callproc('show_artist_cmt', (inputID,))
        each = cursor.fetchone()
        content = {'comment': each[1],
                   'cmtTime': each[2].strftime('%Y-%m-%d'),
                   'numLike': each[3],
                   'userName': each[4]}
        artistRes.append(content)
    with connection.cursor() as cursor:
        cursor.callproc('show_artist_albumlist', (inputID,))
        tmp = []
        for each in cursor.fetchall():
            content = {'albumID': each[0],
                       'albumName': each[1],
                       'releaseDate': each[2].strftime('%Y-%m-%d'),
                       'albumCategory': each[3],
                       'star': each[4],
                       'myCmt': each[5]}
            tmp.append(content)
        artistRes.append(tmp)
    context = {'pic': artistRes[0],
               'info': artistRes[1],
               'details': artistRes[2],
               'cmt': artistRes[3],
               'list': artistRes[4]}
    return render(request, 'artist.html', context)


def showAlbumPage(request, inputID):
    albumRes = []
    with connection.cursor() as cursor:
        cursor.callproc('show_album_pic', (inputID,))
        each = cursor.fetchone()
        content = {'picAddress': each[0]}
        albumRes.append(content)
    with connection.cursor() as cursor:
        cursor.callproc('show_album_info', (inputID,))
        each = cursor.fetchone()
        content = {'albumInfo': each[0]}
        albumRes.append(content)
    with connection.cursor() as cursor:
        cursor.callproc('show_album_details', (inputID,))
        tmp = []
        for each in cursor.fetchall():
            content = {'albumName': each[0],
                       'artistID': each[1],
                       'artistName': each[2],
                       'albumLan': each[3],
                       'recordLabel': each[4],
                       'releaseDate': each[5].strftime('%Y-%m-%d'),
                       'albumCategory': each[6],
                       'genreID': each[7],
                       'genreName': each[8],
                       'star': each[9],
                       'myCmt': each[10],
                       'listenDate': each[11].strftime('%Y-%m-%d')}
            tmp.append(content)
        albumRes.append(tmp)
    with connection.cursor() as cursor:
        cursor.callproc('show_album_cmt', (inputID,))
        each = cursor.fetchone()
        content = {'comment': each[1],
                   'cmtTime': each[2].strftime('%Y-%m-%d'),
                   'numLike': each[3],
                   'userName': each[4]}
        albumRes.append(content)
    with connection.cursor() as cursor:
        cursor.callproc('show_album_songlist', (inputID,))
        tmp = []
        for each in cursor.fetchall():
            content = {'songID': each[0],
                       'songName': each[1],
                       'star': each[2],
                       'myCmt': each[3]}
            tmp.append(content)
        albumRes.append(tmp)
    context = {'pic': albumRes[0],
               'info': albumRes[1],
               'details': albumRes[2],
               'cmt': albumRes[3],
               'list': albumRes[4]}
    return render(request, 'album.html', context)


def showSongPage(request, inputID):
    # print(inputID)
    songRes = []
    with connection.cursor() as cursor:
        cursor.callproc('show_song_pic', (inputID,))
        each = cursor.fetchone()
        content = {'picAddress': each[0]}
        songRes.append(content)
    with connection.cursor() as cursor:
        cursor.callproc('show_song_lyrics', (inputID,))
        for each in cursor.fetchall():
            content = {'songLyrics': each[0]}
            songRes.append(content)
    with connection.cursor() as cursor:
        cursor.callproc('show_song_details', (inputID,))
        for each in cursor.fetchall():
            content = {'songID': each[0],
                       'songName': each[1],
                       'artistID': each[2],
                       'artistName': each[3],
                       'albumID': each[4],
                       'albumName': each[5]}
            songRes.append(content)
    with connection.cursor() as cursor:
        cursor.callproc('show_song_cmt', (inputID,))
        for each in cursor.fetchall():
            content = {'comment': each[1],
                       'cmtTime': each[2].strftime('%Y-%m-%d'),
                       'numLike': each[3],
                       'userName': each[4]}
            songRes.append(content)
    context = {'pic': songRes[0],
               'lyrics': songRes[1],
               'details': songRes[2],
               'cmt': songRes[3]}
    return render(request, 'song.html', context)


def showGenrePage(request, inputID):
    # genreRes = []
    sqlG = "SELECT genreID, genreName, genreInfo FROM Genre WHERE genreID = %s"
    resG = Genre.objects.raw(sqlG, inputID)
    for i in resG:
        content = {'genreID': i.genreID,
                   'genreName': i.genreName,
                   'genreInfo': i.genreInfo}
    context = {'genre': content}
    return render(request, 'genre.html', context)


def search(request):
    return render(request, 'search.html')


def searchArtistByName(request):
    inputName = request.POST.get('artistQuery')
    # print(inputName)
    if Artist.objects.filter(artistName__icontains=inputName):
        # print('yes')
        arr = []
        with connection.cursor() as cursor:
            cursor.callproc('search_artist_by_name', (inputName,))
            for each in cursor.fetchall():
                content = {'picAddress': each[0],
                           'artistID': each[1],
                           'artistName': each[2],
                           'artistReign': each[3]}
                arr.append(content)
        context = {'artistRes': arr}
        return render(request, 'search.html', context)
    return render(request, 'search.html')


def searchAlbumByName(request):
    inputName = request.POST.get('albumQuery')
    if Album.objects.filter(albumName__icontains=inputName):
        arr = []
        with connection.cursor() as cursor:
            cursor.callproc('search_album_by_name', (inputName,))
            for each in cursor.fetchall():
                content = {'picAddress': each[0],
                           'albumID': each[1],
                           'albumName': each[2],
                           'artistID': each[3],
                           'artistName': each[4],
                           'star': each[5],
                           'releaseDate': each[6].strftime('%Y-%m-%d')}
                arr.append(content)
        context = {'albumRes': arr}
        return render(request, 'search.html', context)
    return render(request, 'search.html')


def searchSongByName(request):
    inputName = request.POST.get('songQuery')
    if Song.objects.filter(songName__icontains=inputName):
        arr = []
        with connection.cursor() as cursor:
            cursor.callproc('search_song_by_name', (inputName,))
            for each in cursor.fetchall():
                content = {'picAddress': each[0],
                           'songID': each[1],
                           'songName': each[2],
                           'artistID': each[5],
                           'artistName': each[6],
                           'albumID': each[3],
                           'albumName': each[4]}
                arr.append(content)
        context = {'songRes': arr}
        return render(request, 'search.html', context)
    return render(request, 'search.html')


def find(request):
    sql = "select * from album where albumID='0AM12f06b'"
    # django 也可以执行原生的sql语句
    result0 = Album.objects.raw(sql)
    # result = Album.objects.get(albumID='0AM12f06b')
    # print(result.genreID)
    for result in result0:
        print(result.genreID, result.language, result.release_time)

    # res = Genre.objects.get(genreID=1)
    # res0 = Genre.objects.all()
    # # print(res.comeon.all())

    # 查询name = tom1的数据
    # result = Student.objects.filter(name='lex')
    """
    result为<class 'django.db.models.query.QuerySet'>的对象
    需要进行数据处理
    """
    arr = []
    # for res in res0:
    #     for i in res.comeon.all():
    #         content = {'ID': i.albumID,
    #                    'name': i.album_name,
    #                    'language': i.language,
    #                    'release TIME': i.release_time,
    #                    'l': str(i.genreID)}
    #         arr.append(content)
    # print(arr)
    # print(type(arr))

    return HttpResponse(arr)