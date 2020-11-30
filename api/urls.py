from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserRegisterAPIView,
                    UserTokenAPIView, UserViewSet)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register(
    'titles/(?P<title_id>[^/.]+)/reviews', ReviewViewSet, basename='review')
router.register(
    'titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments', CommentViewSet, basename='comment')
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/email/', UserRegisterAPIView.as_view(), name='user_register'),
    path('auth/token/', UserTokenAPIView.as_view(), name='user_token'),
]
