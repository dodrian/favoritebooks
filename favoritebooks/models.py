from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Book(models.Model):
    class Meta:
        unique_together = ("title", "author")
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.PROTECT)

    def __str__(self):
        return "{}, by {}".format(self.title, self.author)


class Favorite(models.Model):
    class Meta:
        unique_together = ('user', 'book')
    user = models.ForeignKey(User,
                             related_name="favorites",
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    comments = models.TextField()

    def __str__(self):
        return str(self.book)
