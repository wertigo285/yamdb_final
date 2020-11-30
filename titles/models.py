from django.db import models
from django.core.validators import MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=20)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.PositiveIntegerField(validators=[MaxValueValidator(9999)])
    description = models.CharField(max_length=200, blank=True)
    genre = models.ManyToManyField(Genre,  related_name='titles')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name='titles', null=True)

    def __str__(self):
        return self.name
