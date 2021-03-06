from django.db import models


class Artist(models.Model):
    artistID = models.CharField(db_column='artistID', max_length=20, primary_key=True)
    artistName = models.CharField(db_column='artistName', max_length=50)
    genreReign = models.CharField(db_column='artistReign', max_length=50)

    class Meta:
        managed = False
        db_table = 'Artist'

    def __str__(self):
        return self.artistName


class Album(models.Model):
    albumID = models.CharField(db_column='albumID', max_length=20, primary_key=True)
    albumName = models.CharField(db_column='albumName', max_length=255)
    artistID = models.ForeignKey('Artist', db_column='artistID', related_name='+', on_delete=models.DO_NOTHING)
    albumLan = models.CharField(db_column='albumLan', max_length=10)
    releaseDate = models.DateField(db_column='releaseDate')
    albumCategory = models.CharField(db_column='albumCategory', max_length=20)
    recordLabel = models.CharField(db_column='recordLabel', max_length=50)
    star = models.CharField(db_column='star', max_length=10)
    myCmt = models.TextField(db_column='myCmt')
    listenDate = models.DateField(db_column='listenDate')

    class Meta:
        managed = False
        db_table = 'Album'


class Song(models.Model):
    songID = models.CharField(db_column='songID', max_length=20, primary_key=True)
    songName = models.CharField(db_column='songName', max_length=255)
    star = models.CharField(db_column='star', max_length=10)
    myCmt = models.TextField(db_column='myCmt')
    albumID = models.ForeignKey('Album', db_column='albumID', on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Song'


class Genre(models.Model):
    genreID = models.IntegerField(db_column='genreID', primary_key=True)
    genreName = models.CharField(db_column='genreName', max_length=50)
    genreInfo = models.TextField(db_column='genreInfo')

    class Meta:
        managed = False
        db_table = 'Genre'

# class User(models.Model):
#     userID = models.IntegerField(db_column='userID', primary_key=True)
#     location = models.CharField(db_column='location', max_length=50)
#     user_name = models.CharField(db_column='user_name', max_length=50)
#     age = models.IntegerField(db_column='age')
#     gender = models.CharField(db_column='gender', max_length=50)
#     constellation = models.CharField(db_column='constellation', max_length=50)
#     play_count = models.IntegerField(db_column='play_count')
#     join_time = models.DateField(db_column='join_time')
#
#     class Meta:
#         managed = False
#         db_table = 'user'
#
#     def __str__(self):
#         return str(self.userID) + ":" + self.user_name.__str__()



