from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class Movies(models.Model):
    movieId = models.AutoField(primary_key=True)
    movieName = models.CharField(max_length=100 , unique=True)
    def __str__(self):
        return self.movieName

class Critics(models.Model):
    criticId = models.AutoField(primary_key=True)
    criticText = models.TextField(max_length=500)
    criticRating = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movieName = models.ForeignKey(Movies, on_delete=models.CASCADE)


