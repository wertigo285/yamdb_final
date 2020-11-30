from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, ParseError, NotFound
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListCreateAPIView, get_object_or_404)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.tokens import confirmation_code_generator

from .permissions import (IsAdminOrReadOnly, IsAdminRole, IsAuthorOrReadOnly,
                          IsModeratorOrReadOnly)
from .serializers import (CommentSerializer, ReviewSerializer,
                          UserRegisterSerializer, UserSerializer, UserTokenSerializer,
                          CategorySerializer, GenreSerializer, TitleSerializer)
from .filters import TitleFilter

User = get_user_model()


class UserRegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        subject = 'Get API token for your account'
        message = render_to_string('confirmation_code_email.html', {
            'token': confirmation_code_generator.make_token(user)
        })
        user.email_user(subject, message)


class UserTokenAPIView(TokenObtainPairView):
    serializer_class = UserTokenSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=username']
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly | IsAdminOrReadOnly,
                          IsAuthorOrReadOnly | IsModeratorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(
            Title.objects.prefetch_related('reviews'), id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title.objects.prefetch_related('reviews'), id=self.kwargs['title_id'])
        review = title.reviews.filter(author=self.request.user).count()
        if review:
            raise ParseError('Review already exists.')
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly | IsAdminOrReadOnly,
                          IsAuthorOrReadOnly | IsModeratorOrReadOnly]

    def get_review_or_404(self, kwargs):
        try:
            return Review.objects.get(id=kwargs['review_id'], title=kwargs['title_id'])
        except Review.DoesNotExist:
            raise NotFound('Review not found.')

    def get_queryset(self):
        review = self.get_review_or_404(self.kwargs)
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review_or_404(self.kwargs)
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']

    def destroy(self, request, *args, **kwargs):
        slug = kwargs.get('pk')
        instance = get_object_or_404(Category, slug=slug)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']

    def destroy(self, request, *args, **kwargs):
        slug = kwargs.get('pk')
        instance = get_object_or_404(Genre, slug=slug)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
