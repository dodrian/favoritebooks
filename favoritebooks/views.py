from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsOwnerOrAdminOrReadOnly, IsSelforAdminorReadOnly
from .serializers import *
from .models import Favorite, Author, Book


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
#    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsSelforAdminorReadOnly]

    def get_serializer_class(self):
        # staff can edit user profiles
        if self.action == 'create':
            return CreateUserSerializer
        elif self.request.user.is_staff:
            # staff can list and edit user profiles
            # create action uses this for proper password creation
            return EditableUserSerializer
        elif (self.action in ['retrieve', 'update',
                              'partial_update', 'destroy'] and
              self.request.user.pk == self.kwargs.get('pk')):
            # Users can edit own profiles
            return EditableUserSerializer
        else:
            return UserSerializer

    @action(detail=True, methods=['get'])
    def favorites(self, request, pk):
        favorites = Favorite.objects.filter(user_id=pk)
        serializer = FavoriteSerializer(favorites, many=True,
                                        context={'request': request})
        return Response(serializer.data)


class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all().order_by('name')
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all().order_by('title')
    permission_classes = [IsAuthenticatedOrReadOnly]


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteViewSerializer
    permission_classes = [IsAuthenticated & IsOwnerOrAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'quickcreate':
            return FavoriteQuickSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FavoriteSerializer
        else:
            return FavoriteViewSerializer

    def get_queryset(self):
        user = self.request.user
        return user.favorites.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def quickcreate(self, request):
        """ Take author, title, and comment, attempt to match author and book,
            otherwise create them."""
        serializer = FavoriteQuickSerializer(data=request.data)
        if serializer.is_valid():
            author, created = Author.objects.get_or_create(
                        name=serializer.data['author'])
            book, created = Book.objects.get_or_create(
                        author=author, title=serializer.data['title'])
            fav = Favorite.objects.create(user=self.request.user,
                                          book=book,
                                          comments=serializer.data['comments'])
            response = FavoriteViewSerializer(fav, context={'request': request})
            return Response(response.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
