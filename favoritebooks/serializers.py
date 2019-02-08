from django.contrib.auth.models import User
from favoritebooks.models import Author, Book, Favorite
from rest_framework import serializers


class AuthorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Author
        fields = ('url', 'name',)


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ('url', 'title', 'author',)


class BookAndAuthorSerializer(serializers.HyperlinkedModelSerializer):
    """ For viewing books in a user's favorites it's nice to see the
        author's name rather than a link """
    author = serializers.ReadOnlyField(source='author.name')

    class Meta:
        model = Book
        fields = ('url', 'title', 'author',)


class FavoriteViewSerializer(serializers.HyperlinkedModelSerializer):
    book = BookAndAuthorSerializer()

    class Meta:
        model = Favorite
        fields = ('url', 'book', 'comments')


class FavoriteSerializer(serializers.HyperlinkedModelSerializer):
    """ For adding and updating favorites we just need the book URL """
    class Meta:
        model = Favorite
        fields = ('url', 'book', 'comments')

    # def create(self, validated_data):
    #     fav = Favorite(**validated_data)
    #     fav.user = self.context.request.user
    #     fav.save()


class FavoriteQuickSerializer(serializers.HyperlinkedModelSerializer):
    """ Attempts to match book and author to database, else creates them"""
    title = serializers.CharField()
    author = serializers.CharField()
    comments = serializers.CharField()

    class Meta:
        model = Favorite
        fields = ('title', 'author', 'comments')


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print('Creating User...')
        return User.objects.create_user(**validated_data)


class EditableUserSerializer(serializers.HyperlinkedModelSerializer):
    """A user can see their own contact details,
        and update their password"""
    favorites = FavoriteViewSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'favorites', 'password')
        extra_kwargs = {'password': {'write_only': True, 'required': False}}
        read_only_fields = ('username',)

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()
        if hasattr(validated_data, 'password'):
            instance.set_password(validated_data.get('password'))
        return instance


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Users can look at other users' favorite books"""
    favorites = FavoriteViewSerializer(many=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'favorites')
