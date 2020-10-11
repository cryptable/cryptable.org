from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blog import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet)
router.register(r'users', views.UserArticlesViewSet)

urlpatterns = [
    path('', include(router.urls)),
]