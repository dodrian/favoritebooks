from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Favorite, Book, Author


class FavoriteTestCase(APITestCase):
    def setUp(self):
        User.objects.create(username='bob', password='secret')
        a = Author.objects.create(name="Bob's favorite author")
        b = Book.objects.create(title="Bob's favorite book", author=a)

    def test_quickcreatefavorite(self):
        bob = User.objects.get(username='bob')
        qcurl = reverse('favorite-quickcreate')
        response = self.client.post(qcurl,
                                    {'title': 'Book',
                                     'author': 'Person',
                                     'comments': 'Blah'})
        # Not logged in
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=bob)
        self.client.post(qcurl,
                         {'title': 'Book',
                          'author': 'Person',
                          'comments': 'Blah'})
        self.assertEqual(Favorite.objects.filter(user=bob).count(), 1)
        self.assertEqual(Book.objects.count(), 2)
        self.client.post(qcurl,
                         {'title': "Bob's favorite book",
                          'author': "Bob's favorite author",
                          'comments': 'Blah'})
        # assert new favorite has been added
        self.assertEqual(Favorite.objects.filter(user=bob).count(), 2)
        # assert no new book has been added
        self.assertEqual(Book.objects.count(), 2)
