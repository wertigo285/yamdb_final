from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg

from users.tokens import confirmation_code_generator
from titles.models import Category, Genre, Title
from reviews.models import Review, Comment

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class UserTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField()

    default_error_messages = {
        'no_active_account': _('No active account found with the given credentials')
    }

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if not user or not confirmation_code_generator.check_token(user, attrs['confirmation_code']):
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        refresh = RefreshToken.for_user(user)

        return {
            'token': str(refresh.access_token),
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'bio', 'email', 'role']

    def validate_role(self, value):
        user = self.context.get('request').user
        if user.is_admin:
            return value
        raise serializers.ValidationError(
            'Only admin can assign roles to users.')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        model = Review
        fields = ['id', 'text', 'author', 'score', 'pub_date']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['name', 'slug']


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ['name', 'slug']


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, obj):
        self.fields['genre'] = GenreSerializer(many=True)
        self.fields['category'] = CategorySerializer()
        return super().to_representation(obj)

    def get_rating(self, obj):
        return obj.reviews.aggregate(rating=Avg('score'))['rating']
